import frappe
from frappe import _
from frappe.utils import get_url



@frappe.whitelist(allow_guest=True)
def web_logout():
	id_token = frappe.local.session.data.get("id_token")

	frappe.local.login_manager.logout()
	frappe.db.commit()

	if id_token:
		qpass_logout_url = (
			"https://www.stgqpass.gov.qa/idp/public/oidc/end_session"
			f"?id_token_hint={id_token}"
			f"&post_logout_redirect_uri={get_url()}"
		)
		frappe.local.response["type"] = "redirect"
		frappe.local.response["location"] = qpass_logout_url
	else:
		frappe.respond_as_web_page(
			_("Logged Out"),
			_("You have been successfully logged out."),
			indicator_color="green"
		)