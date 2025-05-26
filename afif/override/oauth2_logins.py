import frappe
from frappe import _
from frappe.utils.oauth import SignupDisabledError, get_oauth2_providers, get_oauth2_flow, get_redirect_uri, get_email, redirect_post_login
from frappe.integrations.oauth2_logins import decoder_compat
import base64
import json
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from frappe.core.doctype.user.user import User



@frappe.whitelist(allow_guest=True)
def custom(code: str, state: str):
    """
    Callback for processing code and state for user added providers

    process social login from /api/method/frappe.integrations.custom/<provider>
    """
    path = frappe.request.path[1:].split("/")
    if len(path) == 4 and path[3]:
        provider = path[3]
        # Validates if provider doctype exists
        if frappe.db.exists("Social Login Key", provider):
            custom_login_via_oauth2(provider, code, state, decoder=decoder_compat)



def custom_login_via_oauth2(provider: str, code: str, state: str, decoder: Callable | None = None):
	info = get_info_via_oauth(provider, code, decoder)
	login_oauth_user(info, provider=provider, state=state)
     


def get_info_via_oauth(provider: str, code: str, decoder: Callable | None = None, id_token: bool = False):
    import jwt

    flow = get_oauth2_flow(provider)
    oauth2_providers = get_oauth2_providers()

    client_id = flow.client_id
    client_secret = flow.client_secret

    # Encode client credentials in Base64 as per Basic Auth
    basic_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    auth_header = {"Authorization": f"Basic {basic_auth}"}

    args = {
        "data": {
            "code": code,
            "redirect_uri": get_redirect_uri(provider),
            "grant_type": "authorization_code",
        },
        "headers": auth_header
    }

    if decoder:
        args["decoder"] = decoder

    session = flow.get_auth_session(**args)
	# handle access token error?

    if id_token or provider == "qatarpass":
        parsed_access = json.loads(session.access_token_response.text)
        token = parsed_access["id_token"]
    
    if id_token:
        info = jwt.decode(token, flow.client_secret, options={"verify_signature": False})
    else:
        api_endpoint = oauth2_providers[provider].get("api_endpoint")
        api_endpoint_args = oauth2_providers[provider].get("api_endpoint_args")
        info = session.get(api_endpoint, params=api_endpoint_args).json()

        if provider == "github" and not info.get("email"):
            emails = session.get("/user/emails", params=api_endpoint_args).json()
            email_dict = next(filter(lambda x: x.get("primary"), emails))
            info["email"] = email_dict.get("email")

    if not (info.get("email_verified") or info.get("email") or info.get("emailVerified")):
        frappe.throw(_("Email not verified with {0}").format(provider.title()))
	# handle emailVerified = False error?

    if token:
        info["id_token"] = token

    return info



def login_oauth_user(
	data: dict | str,
	provider: str | None = None,
	state: dict | str | None = None,
	generate_login_token: bool = False,
):
    # json.loads data and state
    if isinstance(data, str):
        data = json.loads(data)

    if isinstance(state, str):
        state = base64.b64decode(state)
        state = json.loads(state.decode("utf-8"))

    if not (state and state["token"]):
        frappe.respond_as_web_page(_("Invalid Request"), _("Token is missing"), http_status_code=417)
        return

    user = get_email(data)

    if not user:
        frappe.respond_as_web_page(
            _("Invalid Request"), _("Please ensure that your profile has an email address")
        )
        return

    try:
        if update_oauth_user(user, data, provider) is False:
            return

    except SignupDisabledError:
        return frappe.respond_as_web_page(
            "Signup is Disabled",
            "Sorry. Signup from Website is disabled.",
            success=False,
            http_status_code=403,
        )

    frappe.local.login_manager.user = user
    frappe.local.login_manager.post_login()

    # Store id_token in session
    id_token = data.pop("id_token", None)
    if id_token:
        frappe.local.session.data["id_token"] = id_token

    # because of a GET request!
    frappe.db.commit()

    if frappe.utils.cint(generate_login_token):
        login_token = frappe.generate_hash(length=32)
        frappe.cache().set_value(f"login_token:{login_token}", frappe.local.session.sid, expires_in_sec=120)

        frappe.response["login_token"] = login_token

    else:
        redirect_to = state.get("redirect_to")
        redirect_post_login(
            desk_user=frappe.local.response.get("message") == "Logged In",
            redirect_to=redirect_to,
            provider=provider,
        )



def update_oauth_user(user: str, data: dict, provider: str):
    if isinstance(data.get("location"), dict):
        data["location"] = data["location"].get("name")

    user: "User" = get_user_record(user, data)
    update_user_record = user.is_new()

    if not user.enabled:
        frappe.respond_as_web_page(_("Not Allowed"), _("User {0} is disabled").format(user.email))
        return False

    if not user.get_social_login_userid(provider):
        update_user_record = True
        match provider:
            case "facebook":
                user.set_social_login_userid(provider, userid=data["id"], username=data.get("username"))
                user.update({"user_image": f"https://graph.facebook.com/{data['id']}/picture"})
            case "google":
                user.set_social_login_userid(provider, userid=data["id"])
            case "github":
                user.set_social_login_userid(provider, userid=data["id"], username=data.get("login"))
            case "frappe" | "office_365":
                user.set_social_login_userid(provider, userid=data["sub"])
            case "salesforce":
                user.set_social_login_userid(provider, userid="/".join(data["sub"].split("/")[-2:]))
            case _:
                user_id_property = (
                    frappe.db.get_value("Social Login Key", provider, "user_id_property") or "sub"
                )
                user.set_social_login_userid(provider, userid=data[user_id_property])

    if update_user_record:
        user.flags.ignore_permissions = True
        user.flags.no_welcome_mail = True

        if default_role := frappe.db.get_single_value("Portal Settings", "default_role"):
            user.add_roles(default_role)

        user.save()

        # Beneficiaries Registration

        frappe.log_error("data", data)
        frappe.log_error("user.name", user.name)
        
        if not frappe.db.exists("Beneficiaries Registration", {"user": user}):
            frappe.get_doc({
                "doctype": "Beneficiaries Registration",
                "user": user.name,
                "en_name": f"{data.get("firstNameEn")} {data.get("middleNameEn")} {data.get("lastNameEn")}",
                "ar_name": f"{data.get("firstNameAr")} {data.get("middleNameAr")} {data.get("lastNameAr")}",
                "date_of_birth": data.get("birthdate"),
                "ben_nationality": frappe.get_value("Country", {"custom_qatarpass_code": data.get("nationality")}, "name"),
                "phone_number": data.get("mobileNumber"),
                "ben_primary_idnumber": data.get("UserQid"),
                "passport_number": data.get("passportNumber"),
                "card_expiry_date": data.get("cardExpiryDate"),
                "passport_expiry_date": data.get("passportExpiryDate")
            }).insert(ignore_permissions=True)
            
        


def get_user_record(user: str, data: dict) -> "User":
    try:
        return frappe.get_doc("User", user)
    except frappe.DoesNotExistError:
        if frappe.get_website_settings("disable_signup"):
            raise SignupDisabledError

    user: "User" = frappe.new_doc("User")

    if gender := data.get("gender", "").title():
        frappe.get_doc({"doctype": "Gender", "gender": gender}).insert(
            ignore_permissions=True, ignore_if_duplicate=True
        )

    user.update(
        {
            "doctype": "User",
            "first_name": get_first_name(data),
            "last_name": get_last_name(data),
            "middle_name": get_middle_name(data),
            "email": get_email(data),
            "gender": gender,
            "enabled": 1,
            "new_password": frappe.generate_hash(),
            "location": data.get("location"),
            "user_type": "Website User",
            "user_image": data.get("picture") or data.get("avatar_url"),
        }
    )

    return user



def get_first_name(data: dict) -> str:
    return data.get("first_name") or data.get("given_name") or data.get("name") or data.get("firstNameEn")



def get_last_name(data: dict) -> str:
    return data.get("last_name") or data.get("family_name") or data.get("lastNameEn")



def get_middle_name(data: dict) -> str:
    return data.get("middleNameEn")