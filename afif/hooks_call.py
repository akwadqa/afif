import frappe
import requests
import json
from datetime import datetime, timedelta, timezone
from frappe.utils import now_datetime, today
# from frappe.utils.background_jobs import enqueue

sanadi_integration_settings = frappe.get_single("Sanadi Integration Settings")

BASE_URL = sanadi_integration_settings.base_url
QID = sanadi_integration_settings.qid
USER_NAME = sanadi_integration_settings.usr_name
PASSWORD = sanadi_integration_settings.pwd


def set_new_user_role_and_lang(doc, method):
    if doc.name != "Administrator":
        doc.role_profile_name = "Beneficiary New Registration"
        if frappe.local.lang:
            doc.language = frappe.local.lang
        doc.save(ignore_permissions=True)


# @frappe.whitelist(allow_guest=True)
# def add_beneficiary(full_name, email, phone_number, personal_id):
#     beneficiary_doc = frappe.get_doc(dict(
#         doctype = 'Beneficiaries',
#         full_name = full_name,
#         email = email,
#         phone_number = phone_number,
#         personal_id = personal_id
#     ))
#     beneficiary_doc.insert(ignore_permissions=True, ignore_mandatory=True)

# def create_user(doc, method):
#     frappe.log_error("create user")
#     if not frappe.db.exists("User", doc.email):
#         from frappe.utils.password import update_password
#         time_zone = frappe.db.get_single_value('System Settings', 'time_zone')
#         user_doc = frappe.get_doc(dict(
#             doctype = 'User',
#             first_name = doc.en_name,
#             email = doc.email,
#             username = doc.email,
#             phone = doc.phone_number,
#             time_zone = time_zone,
#             send_welcome_email = 0,
#             user_type="Website User",
#             roles=[{"doctype": "Has Role", "role": "Beneficiary"}]
#         )).insert(ignore_permissions=True)

#         update_password(user_doc.name, doc.ben_primary_idnumber)

#         doc.user = user_doc.name
#     else:
#         doc.user = doc.email
#     doc.save(ignore_permissions=True)


def link_user(doc, method):
    frappe.log_error("link user")
    doc.user = frappe.session.user
    doc.save(ignore_permissions=True)


# def enqueue_create_new_beneficiary(doc, method):
#     if doc.workflow_state == "Accepted":
#         enqueue("afif.hooks_call.create_new_beneficiary", doc=doc)


# set status to Updated
def updated_status(doc, method):
    query = f""" select status from `tabBeneficiaries Registration` where name="{doc.name}" """
    status = frappe.db.sql(query)
    if status:
        status = status[0][0]
        if doc.workflow_state == "Not Accepted" and status == "Not Accepted":
            doc.status = "Updated"
            doc.workflow_state = "Updated"
            # query = f"""update `tabBeneficiaries Registration` set `status`="Updated"
            #             where name="{doc.name}" """
            # frappe.db.sql(query)
            # frappe.db.commit()
            # doc.reload()
    
    # # Not Accepted exception
    # query = f""" select workflow_state from `tabBeneficiaries Registration` where name="{doc.name}" """
    # workflow_state = frappe.db.sql(query)
    # if workflow_state:
    #     workflow_state = workflow_state[0][0]
    #     if doc.workflow_state == "Not Accepted" and workflow_state != "Not Accepted":
    #         query = f"""update `tabBeneficiaries Registration` set `show_create_rejection_note_button`=1
    #             where name="{doc.name}" """
    #         frappe.db.sql(query)
    #         frappe.db.commit()
    #         frappe.throw("In order to Reject, please create and submit a Rejection Note.")


    # if doc.workflow_state == "Not Accepted":
    #     # doc.workflow_state = "Updated"
        # query = f"""update `tabBeneficiaries Registration` set `workflow_state`="Updated"
        #             where name="{doc.name}" """
        # frappe.db.sql(query)
        # frappe.db.commit()
        # doc.reload()

 
    # # Not Accepted exception
    # query = f""" select workflow_state from `tabBeneficiaries Registration` where name="{doc.name}" """
    # workflow_state = frappe.db.sql(query)
    # if workflow_state:
    #     workflow_state = workflow_state[0][0]
    #     if workflow_state == "Rejected Without Note":
    #         frappe.throw("In order to Reject, please create and submit a Rejection Note.")


# # set workflow_state and status to Not Accepted when Rejection Note is submitted
# def update_workflow_state(doc, method):
#     query = f"""update `tabBeneficiaries Registration` set `workflow_state`="Not Accepted", `status`="Not Accepted"
#                 where name="{doc.beneficiaries_rejection}" """
#     frappe.db.sql(query)
#     frappe.db.commit()

#     ben_reg_doc = frappe.get_doc("Beneficiaries Registration", doc.beneficiaries_rejection)
#     ben_reg_doc.reload()

#     # update role to Beneficiary Not Accepted
#     frappe.log_error("update role - Not Accepted")
#     if doc.user != "Administrator":
#         user_doc = frappe.get_doc("User", doc.user)
#         user_doc.role_profile_name = "Beneficiary Not Accepted"
#         user_doc.save(ignore_permissions=True)


def rejection_note(doc, method):
    if doc.workflow_state == "Not Accepted" and not doc.custom_notes:
        frappe.throw("The field 'Notes' must be filled in to reject the registration.")


def create_new_beneficiary(doc, method):
    frappe.log_error("create_new_beneficiary")
    if doc.workflow_state == "Accepted":
        # frappe.sendmail(
        #     recipients=doc.email,
        #     subject="AFIF - Beneficiary Registration",
        #     message="Status - Accepted"
        # )

        # update role to Beneficiary Accepted
        frappe.log_error("update role")
        if doc.user != "Administrator":
            user_doc = frappe.get_doc("User", doc.user)
            user_doc.role_profile_name = "Beneficiary Accepted"
            user_doc.save(ignore_permissions=True)

        # Authentication
        url = f"{BASE_URL}eservices/api/v2/sanadi/auth/integration/login"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "userName": USER_NAME,
            "userPassword": PASSWORD,
            "qId": QID,
            "lang": "EN"
        }

        response_auth = requests.post(url=url, data=json.dumps(body), headers=headers, verify=False)

        if response_auth.status_code == 200:
            msg = f"Authentication response success: {response_auth.json()}"
            frappe.log_error("authentication response", msg)

            # Validate Token
            url = f"{BASE_URL}eservices/api/v2/sanadi/auth/validate-token"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": response_auth.json().get('rs').get('token')
            }

            response_val = requests.post(url=url, headers=headers, verify=False)

            if response_val.status_code == 200:
                msg = f"Validate response success: {response_val.json()}"
                frappe.log_error("validate response", msg)

                # Create new beneficiary
                url = f"{BASE_URL}eservices/api/v2/sanadi/aids/beneficiary?with-check=false"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": response_auth.json().get('rs').get('token')
                }

                nationality = frappe.get_value("Country", doc.ben_nationality, "sanadi_code")
                ben_primary_idtype = get_idtype(doc.ben_primary_idtype)
                gender = get_gender(doc)
                education_level = get_education_level(doc)
                if doc.visa_type != "Visit":
                    occupation_status = get_occupation_status(doc)
                else:
                    occupation_status = 0
                marital_status = get_marital_status(doc)
                if doc.requestor_idtype:
                    requestor_idtype = get_idtype(doc.requestor_idtype)
                else:
                    requestor_idtype = None
                if doc.ben_sec_idtype:
                    ben_sec_idtype = get_idtype(doc.ben_sec_idtype)
                else:
                    ben_sec_idtype = None
                if doc.requestor_nationality:
                    requestor_nationality = frappe.get_value("Country", doc.requestor_nationality, "sanadi_code")
                else:
                    requestor_nationality = None
                if doc.ben_sec_nationality:
                    ben_sec_nationality = frappe.get_value("Country", doc.ben_sec_nationality, "sanadi_code")
                else:
                    ben_sec_nationality = None
                ben_requestor_relationtype =  get_ben_requestor_relationtype(doc)
                residence_city = get_residence_city(doc)

                beneficiary_obligation_set = get_beneficiary_obligation_set(doc)
                beneficiary_income_set = get_beneficiary_income_set(doc)


                # Get the current date and time in the UTC timezone
                now = datetime.now()
                # Format the date and time as a string in the desired format
                formatted_date_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                body = {
                    "arName": doc.ar_name,
                    "enName": doc.en_name,
                    "beneficiaryObligationSet": beneficiary_obligation_set,
                    "beneficiaryIncomeSet": beneficiary_income_set,
                    "benNationality": nationality,
                    "benPrimaryIdType": ben_primary_idtype,
                    "benPrimaryIdNumber": doc.ben_primary_idnumber,
                    "benPrimaryIdNationality": nationality,
                    "benSecIdType": ben_sec_idtype,
                    "benSecIdNationality": ben_sec_nationality,
                    "benSecIdNumber": doc.ben_sec_idnumber,
                    "gender": gender,
                    "dateOfBirth": str(doc.date_of_birth),
                    "educationLevel": education_level,
                    "phoneNumber1": doc.phone_number,
                    "residenceCity": residence_city,
                    "zone": doc.zone,
                    "buildingName": doc.building_name,
                    "unit": doc.unit,
                    "occuption": doc.occupation if doc.occupation else None,
                    "occuptionStatus": occupation_status,
                    "employeer": doc.employer_name if doc.employer_name else "None",
                    "streetName": doc.street_name,
                    "addressDescription": doc.adress,
                    "employeerAddress": doc.employer_address,
                    "employeerMobileNumber": None,
                    "employeerEmail": None,
                    "govEmploymentStatus": None,
                    "govEmploymentType": None,
                    "govEmploymentTypeInfo": None,
                    "govOccupationName": None,
                    "govEmploymentStartDate": None,
                    "govEmployementEndDate": None,
                    "maritalStatus": marital_status,
                    "benWivesCount": None,
                    "benDependentsCount": doc.ben_dependent_count,
                    "familyCount": doc.family_size,
                    "benRequestorRelationType": ben_requestor_relationtype,
                    "requestorName": doc.requestor_name,
                    "requestorIdType": requestor_idtype,
                    "requestorIdNumber": doc.requestor_idnumber,
                    "requestorIdNationality": requestor_nationality,
                    "requestorPhoneNumber": doc.requestor_number,
                    "statusDateModified": formatted_date_time
                }
                frappe.log_error("body", body)

                response_ben = requests.post(url=url, headers=headers, data=json.dumps(body), verify=False)

                if response_ben.status_code == 200:
                    msg = f"Beneficiary response success: {response_ben.json()}"
                    frappe.log_error("beneficiary response", msg)

                    if response_ben.json().get('rs').get('first') == 'SAVED':
                        ben_id = response_ben.json().get('rs').get('second').get('id')
                        query = f"""update `tabBeneficiaries Registration` set `ben_id`={ben_id}
                            where name="{doc.name}" """
                        frappe.db.sql(query)
                        frappe.db.commit()

                else:
                    msg = f"Beneficiary response fail: {response_ben.json()}"
                    frappe.log_error("beneficiary response", msg)
                    frappe.throw("Beneficiary registration failed.")
                
            else:
                msg = f"Validate response fail: {response_val.json()}"
                frappe.log_error("validate response", msg)

        else:
            msg = f"Authentication response fail: {response_auth.json()}"
            frappe.log_error("authentication response", msg)
    
    
    elif doc.workflow_state == "Not Accepted":
        # update role to Beneficiary Not Accepted
        frappe.log_error("update role - Not Accepted")
        if doc.user != "Administrator":
            user_doc = frappe.get_doc("User", doc.user)
            user_doc.role_profile_name = "Beneficiary Not Accepted"
            user_doc.save(ignore_permissions=True)

    elif doc.workflow_state == "New Registration":
        # update role to Beneficiary Submitted
        frappe.log_error("update role")
        if doc.user != "Administrator":
            user_doc = frappe.get_doc("User", doc.user)
            user_doc.role_profile_name = "Beneficiary New Registration"
            user_doc.save(ignore_permissions=True)
        
    elif doc.workflow_state == "Updated":
        # update role to Beneficiary Updated
        frappe.log_error("update role")
        if doc.user != "Administrator":
            user_doc = frappe.get_doc("User", doc.user)
            user_doc.role_profile_name = "Beneficiary Updated"
            user_doc.save(ignore_permissions=True)

    # elif doc.workflow_state == "Not Accepted" and doc.rejection_note:
    #     message = f"Dear {doc.en_name},<br><br>\
    #         Id: {doc.ben_primary_idnumber}<br><br>\
    #         {doc.name}<br><br>\
    #         Registration: {doc.workflow_state}<br><br>\
    #         Kindly follow the bellow instructions and resubmit your registration:<br><br>\
    #         {doc.rejection_note}<br><br>\
    #         Kindly,<br><br>\
    #         Afif Support Team"

    #     frappe.sendmail(
    #         recipients=doc.email,
    #         subject="AFIF - Beneficiary Registration",
    #         message=message
    #     )


def get_idtype(doc):
    if doc == "Qatari Id":
        idtype = 1
    elif doc == "Passport":
        idtype = 3
    elif doc == "GCC Id":
        idtype = 2
    elif doc == "Visa Number":
        idtype = 4
    else:
        idtype = None
    
    return idtype


def get_gender(doc):
    if doc.gender == "Male":
        gender = 1
    elif doc.gender == "Female":
        gender = 2

    return gender       
	

def get_education_level(doc):
    if doc.education_level == "Ignorant":
        education_level = 1
    elif doc.education_level == "Primary School Graduate":
        education_level = 2
    elif doc.education_level == "Industrial School":
        education_level = 6
    elif doc.education_level == "Secondary School Graduate":
        education_level = 3
    elif doc.education_level == "High Education Level":
        education_level = 4
    elif doc.education_level == "Above High Education Level":
        education_level = 5
    
    return education_level


def get_occupation_status(doc):
    if doc.currently_working == "Yes":
        occupation_status = 1
    elif doc.currently_working == "No":
        occupation_status = 2
    
    return occupation_status


def get_marital_status(doc):
    if doc.marital_status == "Married":
        marital_status = 2
    elif doc.marital_status == "Widowed":
        marital_status = 4
    elif doc.marital_status == "Divorced":
        marital_status = 3
    elif doc.marital_status == "Single":
        marital_status = 1
    elif doc.marital_status == "Separated":
        marital_status = 5
    
    return marital_status


def get_ben_requestor_relationtype(doc):
    if doc.ben_requestor_relationtype == "Relative to the subvention requestor":
        ben_requestor_relationtype = 2
    elif doc.ben_requestor_relationtype == "The same subvention requestor":
        ben_requestor_relationtype = 1
    
    return ben_requestor_relationtype


def get_residence_city(doc):
    if doc.city == "Doha":
        residence_city = 1
    elif doc.city == "AL Khoar":
        residence_city = 3
    elif doc.city == "Al Daayen":
        residence_city = 4
    elif doc.city == "Umm Salal":
        residence_city = 5
    elif doc.city == "Al Wakra":
        residence_city = 8
    elif doc.city == "Al Rayan":
        residence_city = 7
    elif doc.city == "Ash Shamal":
        residence_city = 2
    elif doc.city == "AL Shehanyia":
        residence_city = 6

    return residence_city


def get_beneficiary_obligation_set(doc):
    beneficiary_obligation_set = []
    if doc.rent_obligation == 1:
        beneficiary_obligation_set.append(
            {
                "installmentsCount": doc.rent_obligations_installments_count,
                "periodicType": get_periodic_type(doc.rent_obligation_periodicity),
                "benObligationType": 1,
                "amount": doc.rent_amount,
                "notes": doc.rent_obligations_note
            }
        )

    if doc.family_obligation == 1:
        beneficiary_obligation_set.append(
            {
                "installmentsCount": doc.family_obligations_installments_count,
                "periodicType": get_periodic_type(doc.family_obligation_periodicity),
                "benObligationType": 4,
                "amount": doc.family_expenses,
                "notes": doc.family_obligations_note
            }
        )

    if doc.debt_obligation == 1:
        beneficiary_obligation_set.append(
            {
                "installmentsCount": doc.debt_obligations_installments_count,
                "periodicType": get_periodic_type(doc.debt_obligation_periodicity),
                "benObligationType": 5,
                "amount": doc.bank_payments_amount,
                "notes": doc.debt_obligations_note
            }
        )

    if doc.treatment_obligation == 1:
        beneficiary_obligation_set.append(
            {
                "installmentsCount": doc.treatment_obligation_installments_count,
                "periodicType": get_periodic_type(doc.treatment_obligation_periodicity),
                "benObligationType": 3,
                "amount": doc.treatment_amount,
                "notes": doc.treatment_obligations_note
            }
        )

    if doc.tuition_obligation == 1:
        beneficiary_obligation_set.append(
            {
                "installmentsCount": doc.tuition_obligation_installments_count,
                "periodicType": get_periodic_type(doc.tuition_obligation_periodicity),
                "benObligationType": 2,
                "amount": doc.tuition_amount,
                "notes": doc.tuition_obligations_note
            }
        )

    # if doc.other_expenses:
    #     beneficiary_obligation_set.append(
    #         {
    #             "installmentsCount": doc.obligations_installments_count,
    #             "periodicType": get_periodic_type(doc.obligation_periodicity),
    #             "benObligationType": 6,
    #             "amount": doc.other_expenses,
    #             "notes": doc.obligation_notes
    #         }
    #     )
    
    return beneficiary_obligation_set


def get_beneficiary_income_set(doc):
    beneficiary_income_set = []
    if doc.ben_income == 1:
        beneficiary_income_set.append(
            {
                "periodicType": get_income_periodic_type(doc.ben_periodic_type),
                "benIncomeType": 1,
                "amount": doc.salary_amount,
                "notes": doc.benficiary_note
            }
        )

    if doc.family_income == 1:
        beneficiary_income_set.append(
            {
                "periodicType": get_income_periodic_type(doc.family_periodic_type),
                "benIncomeType": 5,
                "amount": doc.family_income_amount,
                "notes": doc.family_note
            }
        )

    if doc.children_income == 1:
        beneficiary_income_set.append(
            {
                "periodicType": get_income_periodic_type(doc.children_periodic_type),
                "benIncomeType": 5,
                "amount": doc.family_children_salary,
                "notes": doc.children_note
            }
        )

    if doc.family_extra == 1:
        beneficiary_income_set.append(
            {
                "periodicType": get_income_periodic_type(doc.extra_periodic_type),
                "benIncomeType": 5,
                "amount": doc.family_extra_salary,
                "notes": doc.family_extra_note
            }
        )
    
    if doc.private_income == 1:
        beneficiary_income_set.append(
            {
                "periodicType": get_income_periodic_type(doc.private_business_periodicity),
                "benIncomeType": 2,
                "amount": doc.private_business_amount,
                "notes": doc.private_note
            }
        )

    if doc.stock_income == 1:
        beneficiary_income_set.append(
            {
                "periodicType": get_income_periodic_type(doc.stock_market_periodicity),
                "benIncomeType": 3,
                "amount": doc.stock_market_income,
                "notes": doc.stock_market_note
            }
        )

    if doc.rent_income == 1:
        beneficiary_income_set.append(
            {
                "periodicType": get_income_periodic_type(doc.rent_periodic_type),
                "benIncomeType": 4,
                "amount": doc.rent_income_amount,
                "notes": doc.rent_note
            }
        )

    return beneficiary_income_set





def before_insert_request(doc, method):
    frappe.log_error("before_insert_request")
    user = frappe.session.user
    if frappe.get_value("Beneficiaries Registration", {"user": user}, "workflow_state") == "Accepted":

        beneficiary = frappe.get_value("Beneficiaries Registration", {"user": user}, "name")

        try:
            last_created_request = frappe.get_last_doc("Beneficiary Request", filters={"beneficiaries": beneficiary})
        except frappe.DoesNotExistError:
            last_created_request = None
        if last_created_request and last_created_request.workflow_state not in ["Rejected by Supervisor", "Rejected", "Approved", "Approved For Aid"]:
            frappe.throw("A previous request is pending review.")
        else:
            # set request ben id
            doc.beneficiaries = beneficiary
            doc.request_date = now_datetime()

    else:
        frappe.throw("Beneficiary is Not Accepted. Refer to your email and update your registration.")

    # doc.save(ignore_permissions=True)


def new_subvention_request(doc, method):
    frappe.log_error("subvention_request")
    if doc.workflow_state == "Pending Specialist Approval":
        # Authentication
        url = f"{BASE_URL}eservices/api/v2/sanadi/auth/integration/login"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "userName": USER_NAME,
            "userPassword": PASSWORD,
            "qId": QID,
            "lang": "EN"
        }

        response_auth = requests.post(url=url, data=json.dumps(body), headers=headers, verify=False)

        if response_auth.status_code == 200:
            msg = f"Authentication response success: {response_auth.json()}"
            frappe.log_error("authentication response", msg)

            # Validate Token
            url = f"{BASE_URL}eservices/api/v2/sanadi/auth/validate-token"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": response_auth.json().get('rs').get('token')
            }

            response_val = requests.post(url=url, headers=headers, verify=False)

            if response_val.status_code == 200:
                msg = f"Validate response success: {response_val.json()}"
                frappe.log_error("validate response", msg)

                # save new request
                url = f"{BASE_URL}eservices/api/v2/sanadi/aids/subvention-request"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": response_auth.json().get('rs').get('token')
                }

                # Get the current date and time in the UTC timezone
                now = datetime.now()
                # Subtract one day from the current date
                one_day_ago = now - timedelta(days=1)
                # Format the date and time as a string in the desired format
                formatted_date_time = one_day_ago.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

                aid_lookup_parent_id, aid_lookup_id = get_aid_lookup_parent_id(doc)
                
                body = {
                    "creationDate": formatted_date_time,  
                    "benId": frappe.get_value("Beneficiaries Registration", doc.beneficiaries, "ben_id"),
                    "requestChannel": 1, 
                    "requestedAidAmount": doc.requested_amount, 
                    "requestSummary": doc.request_summary, 
                    "aidLookupId": aid_lookup_id, 
                    "aidLookupParentId": aid_lookup_parent_id
                }
                
                frappe.log_error("body", body)

                response_req = requests.post(url=url, headers=headers, data=json.dumps(body), verify=False)

                if response_req.status_code == 200:
                    msg = f"Subvention response success: {response_req.json()}"
                    frappe.log_error("subvention response", msg)


                    subvention_request_id = response_req.json().get('rs').get('id')
                    query = f"""update `tabBeneficiary Request` set `request_id`={subvention_request_id}
                        where name="{doc.name}" """
                    frappe.db.sql(query)
                    frappe.db.commit()

                    subvention_request_serial = response_req.json().get('rs').get('requestSerial')
                    query = f"""update `tabBeneficiary Request` set `request_serial`={subvention_request_serial}
                        where name="{doc.name}" """
                    frappe.db.sql(query)
                    frappe.db.commit()

                    subvention_request_full_serial = response_req.json().get('rs').get('requestFullSerial')
                    frappe.log_error("subvention response", subvention_request_full_serial)
                    query = f"""update `tabBeneficiary Request` set `request_fullserial`='{subvention_request_full_serial}'
                        where name="{doc.name}" """
                    frappe.db.sql(query)
                    frappe.db.commit()

                else:
                    msg = f"Subvention response fail: {response_req.json()}"
                    frappe.log_error("subvention response", msg)
                
            else:
                msg = f"Validate response fail: {response_val.json()}"
                frappe.log_error("validate response", msg)

        else:
            msg = f"Authentication response fail: {response_auth.json()}"
            frappe.log_error("authentication response", msg)

    # elif doc.workflow_state == "Rejected by Supervisor":
    #     frappe.sendmail(
    #         recipients=frappe.get_value("Beneficiaries Registration", doc.beneficiaries, "email"),
    #         subject="AFIF - Beneficiary Request",
    #         message="Status - Rejected by Supervisor"
    #     )



def get_aid_lookup_parent_id(doc):
    if doc.request_category == "Medical Assistance":
        aid_lookup_parent_id = 10020
        if doc.medical_assistance == "Medication":
             aid_lookup_id = 1002020
        elif doc.medical_assistance == "Medical Procedures":
             aid_lookup_id = 1002010
        elif doc.medical_assistance == "Medical Supplies":
             aid_lookup_id = 1002030
        elif doc.medical_assistance == "Medical Equipment":
             aid_lookup_id = 1002040
        elif doc.medical_assistance == "Natural Treatment":
             aid_lookup_id = 1002050
        elif doc.medical_assistance == "Other Medical Assistance":
             aid_lookup_id = 1002060

    elif doc.request_category == "Social Assistance":
        aid_lookup_parent_id = 10030
        if doc.social_assistance == "Garmeen":
             aid_lookup_id = 1003010
        elif doc.social_assistance == "Orphan sponsorship":
             aid_lookup_id = 1003020
        elif doc.social_assistance == "Marriage assistance":
             aid_lookup_id = 1003030
        elif doc.social_assistance == "Economic empowerment assistance":
             aid_lookup_id = 1003040
        elif doc.social_assistance == "Travel ticket assistance":
             aid_lookup_id = 1003050
        elif doc.social_assistance == "Widow assistance":
             aid_lookup_id = 1003060
        elif doc.social_assistance == "Divorced women assistance":
             aid_lookup_id = 1003070
        elif doc.social_assistance == "Elderly assistance":
             aid_lookup_id = 1003080
        elif doc.social_assistance == "Unemployed assistance":
             aid_lookup_id = 1003090
        elif doc.social_assistance == "Visitor assistance":
             aid_lookup_id = 10030100
        elif doc.social_assistance == "Emergency assistance":
             aid_lookup_id = 10030110
        elif doc.social_assistance == "Psychological support assistance":
             aid_lookup_id = 10030120
        elif doc.social_assistance == "Other social assistance":
             aid_lookup_id = 10030130

    elif doc.request_category == "Education Assistance":
        aid_lookup_parent_id = 10010
        if doc.educational_assistance == "Tuition Fees":
             aid_lookup_id = 1001010
        elif doc.educational_assistance == "Transportation Fees":
             aid_lookup_id = 1001020
        elif doc.educational_assistance == "Books And Resources":
             aid_lookup_id = 1001030
        elif doc.educational_assistance == "Educational Equipment":
             aid_lookup_id = 1001040
        elif doc.educational_assistance == "Other Educational Assistance":
             aid_lookup_id = 1001050

    elif doc.request_category == "Family Assistance":
        aid_lookup_parent_id = 20010
        if doc.family_assistance == "Emergency lump-sum financial assistance":
             aid_lookup_id = 2001010
        elif doc.family_assistance == "Monthly financial assistance":
             aid_lookup_id = 2001020
        elif doc.family_assistance == "In-kind assistance":
             aid_lookup_id = 2001030
        elif doc.family_assistance == "Family nursery sponsorship":
             aid_lookup_id = 2001040
        elif doc.family_assistance == "Seasonal financial assistance":
             aid_lookup_id = 2001050
        elif doc.family_assistance == "Food basket (food aid)":
             aid_lookup_id = 2001060
        elif doc.family_assistance == "In-kind assistance with a monthly shopping card":
             aid_lookup_id = 2001070
        elif doc.family_assistance == "In-kind assistance with a Ramadan shopping card":
             aid_lookup_id = 2001080
        elif doc.family_assistance == "Utility bills":
             aid_lookup_id = 2001090
        elif doc.family_assistance == "Fines support":
             aid_lookup_id = 20010100
        elif doc.family_assistance == "Other family assistance":
             aid_lookup_id = 20010110

    elif doc.request_category == "Housing Assistance":
        aid_lookup_parent_id = 20020
        if doc.housing_assistance == "Rent support":
             aid_lookup_id = 2002010
        elif doc.housing_assistance == "Land purchase":
             aid_lookup_id = 2002020
        elif doc.housing_assistance == "Real estate purchase":
             aid_lookup_id = 2002030
        elif doc.housing_assistance == "Land purchase and construction":
             aid_lookup_id = 2002040
        elif doc.housing_assistance == "Demolition and construction":
             aid_lookup_id = 2002050
        elif doc.housing_assistance == "Maintenance and restoration":
             aid_lookup_id = 2002060
        elif doc.housing_assistance == "Furnishing support":
             aid_lookup_id = 2002070
        elif doc.housing_assistance == "Other social housing assistance":
             aid_lookup_id = 2002080

    elif doc.request_category == "Training Assistance":
        aid_lookup_parent_id = 30010
        if doc.training_assistance == "Secretarial training":
            aid_lookup_id = 3001010
        elif doc.training_assistance == "Entrepreneurship training":
            aid_lookup_id = 3001020
        elif doc.training_assistance == "Student training":
            aid_lookup_id = 3001030
        elif doc.training_assistance == "Prisoner training":
            aid_lookup_id = 3001040
        elif doc.training_assistance == "Other training and rehabilitation":
            aid_lookup_id = 3001050

    elif doc.request_category == "Awareness Assistance":
        aid_lookup_parent_id = 30020
        if doc.awareness_assistance == "National Awareness":
             aid_lookup_id = 3002010
        elif doc.awareness_assistance == "Cultural Awareness":
             aid_lookup_id = 3002020
        elif doc.awareness_assistance == "Social Awareness":
             aid_lookup_id = 3002030
        elif doc.awareness_assistance == "Health Awareness":
             aid_lookup_id = 3002040
        elif doc.awareness_assistance == "Environmental Awareness":
             aid_lookup_id = 3002050
        elif doc.awareness_assistance == "Charitable Awareness":
             aid_lookup_id = 3002060
        elif doc.awareness_assistance == "Consumer Awareness":
             aid_lookup_id = 3002070
        elif doc.awareness_assistance == "Other Awareness Assistance":
             aid_lookup_id = 3002080

    return aid_lookup_parent_id, aid_lookup_id





# def update_subvention_request(doc, method):
#     frappe.log_error("update subvention_request")
#     # Authentication
#     url = "https://api.raca.gov.qa/eservices/api/v2/sanadi/auth/integration/login"
#     headers = {
#         "Content-Type": "application/json"
#     }
#     body = {
        #     "userName": "int_afif",
        #     "userPassword": "TRu_osaRA4+1",
        #     "qId": 28981808830,
        #     "lang": "EN"
        # }

#     response_auth = requests.post(url=url, data=json.dumps(body), headers=headers, verify=False)

#     if response_auth.status_code == 200:
#         msg = f"Authentication response success: {response_auth.json()}"
#         frappe.log_error("authentication response", msg)

#         # Validate Token
#         url = "https://stgapi.raca.gov.qa/eservices/api/v2/sanadi/auth/validate-token"
#         headers = {
#             "Accept": "application/json",
#             "Content-Type": "application/json",
#             "Authorization": response_auth.json().get('rs').get('token')
#         }

#         response_val = requests.post(url=url, headers=headers, verify=False)

#         if response_val.status_code == 200:
#             msg = f"Validate response success: {response_val.json()}"
#             frappe.log_error("validate response", msg)

#             # update request
#             url = "https://stgapi.raca.gov.qa/eservices/api/v2/sanadi/aids/subvention-request"
#             headers = {
#                 "Content-Type": "application/json",
#                 "Authorization": response_auth.json().get('rs').get('token')
#             }

#             # Get the current date and time in the UTC timezone
#             now = datetime.now()
#             # Format the date and time as a string in the desired format
#             formatted_date_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f%z")

#             aid_lookup_parent_id, aid_lookup_id = get_aid_lookup_parent_id(doc)

#             body = {
#                 "benId": frappe.get_value("Beneficiaries Registration", doc.beneficiaries, "ben_id"),
#                 "requestSerial": doc.request_serial,
#                 "requestFullSerial": doc.request_full_serial,
#                 "requestChannel": 1,
#                 "requestedAidAmount": doc.requested_amount,
#                 "requestSummary": doc.request_summary,
#                 "creationDate": formatted_date_time,
#                 "status": 2,
#                 "orgId": 85,
#                 "orgUserId": 509,
#                 "aidLookupId": aid_lookup_id,
#                 "aidLookupParentId": aid_lookup_parent_id,
#                 "id": doc.request_id
#             }
            
#             frappe.log_error("body", body)

#             response_put = requests.put(url=url, headers=headers, data=json.dumps(body), verify=False)

#             if response_put.status_code == 200:
#                 msg = f"Update response success: {response_put.json()}"
#                 frappe.log_error("update response", msg)

#             else:
#                 msg = f"Update response fail: {response_put.json()}"
#                 frappe.log_error("update response", msg)

#         else:
#             msg = f"Validate response fail: {response_val.json()}"
#             frappe.log_error("validate response", msg)

#     else:
#         msg = f"Authentication response fail: {response_auth.json()}"
#         frappe.log_error("authentication response", msg)




def update_subvention_request_status(doc, method):
    frappe.log_error("update subvention_request status")

    if doc.workflow_state == "Rejected" or doc.workflow_state == "Approved":
        # Authentication
        url = f"{BASE_URL}eservices/api/v2/sanadi/auth/integration/login"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "userName": USER_NAME,
            "userPassword": PASSWORD,
            "qId": QID,
            "lang": "EN"
        }

        response_auth = requests.post(url=url, data=json.dumps(body), headers=headers, verify=False)

        if response_auth.status_code == 200:
            msg = f"Authentication response success: {response_auth.json()}"
            frappe.log_error("authentication response", msg)

            # Validate Token
            url = f"{BASE_URL}eservices/api/v2/sanadi/auth/validate-token"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": response_auth.json().get('rs').get('token')
            }

            response_val = requests.post(url=url, headers=headers, verify=False)

            if response_val.status_code == 200:
                msg = f"Validate response success: {response_val.json()}"
                frappe.log_error("validate response", msg)

                # update request status
                if doc.workflow_state == "Rejected":
                    url = f"{BASE_URL}eservices/api/v2/sanadi/aids/subvention-request/cancel"
                elif doc.workflow_state == "Approved":
                    url = f"{BASE_URL}eservices/api/v2/sanadi/aids/subvention-request/approve"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": response_auth.json().get('rs').get('token')
                }
                body = {
                    "requestId": doc.request_id,
                    "reason": "Approved" if doc.workflow_state == "Approved" else "Rejected"
                }
                frappe.log_error("body", body)

                response_put_status = requests.put(url=url, headers=headers, data=json.dumps(body), verify=False)

                if response_put_status.status_code == 200:
                    msg = f"Update status response success: {response_put_status.json()}"
                    frappe.log_error("update status response", msg)

                else:
                    msg = f"Update status response fail: {response_put_status.json()}"
                    frappe.log_error("update status response", msg)

            else:
                msg = f"Validate response fail: {response_val.json()}"
                frappe.log_error("validate response", msg)

        else:
            msg = f"Authentication response fail: {response_auth.json()}"
            frappe.log_error("authentication response", msg)

    # if doc.workflow_state == "Rejected":
    #     frappe.sendmail(
    #         recipients=frappe.get_value("Beneficiaries Registration", doc.beneficiaries, "email"),
    #         subject="AFIF - Beneficiary Request",
    #         message="Status - Rejected"
    #     )


			


# def set_suggested_amount(doc, method):
#     frappe.log_error("set_suggested_amount")
#     if doc.beneficiary_request:
#         query = f"""update `tabBeneficiary Aid` set `suggested_amount`={frappe.get_value("Beneficiary Request", doc.beneficiary_request, "approved_amount")}
#             where name="{doc.name}" """
#         frappe.db.sql(query)
#         frappe.db.commit()


def set_aid_amount(doc, method):
    frappe.log_error("set_aid_amount")
    if len(doc.committee_amount) > 0:
        total_amount = 0
        for amount in doc.committee_amount:
            total_amount += float(amount.suggested_amount)
        average_amount = total_amount/int(len(doc.committee_amount))

        if average_amount > float(frappe.get_value("Beneficiary Request", doc.beneficiary_request, "approved_amount")):
            frappe.throw("Aid Amount can't be more than Approved Amount")

        query = f"""update `tabBeneficiary Aid` set `aid_amount`={average_amount}
            where name="{doc.name}" """
        frappe.db.sql(query)
        frappe.db.commit()


def new_aid_request(doc, method):
    frappe.log_error("new aid request")
    if doc.workflow_state == "Approved":
        # Authentication
        url = f"{BASE_URL}eservices/api/v2/sanadi/auth/integration/login"
        headers = {
            "Content-Type": "application/json"
        }
        body = {
            "userName": USER_NAME,
            "userPassword": PASSWORD,
            "qId": QID,
            "lang": "EN"
        }

        response_auth = requests.post(url=url, data=json.dumps(body), headers=headers, verify=False)

        if response_auth.status_code == 200:
            msg = f"Authentication response success: {response_auth.json()}"
            frappe.log_error("authentication response", msg)

            # Validate Token
            url = f"{BASE_URL}eservices/api/v2/sanadi/auth/validate-token"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": response_auth.json().get('rs').get('token')
            }

            response_val = requests.post(url=url, headers=headers, verify=False)

            if response_val.status_code == 200:
                msg = f"Validate response success: {response_val.json()}"
                frappe.log_error("validate response", msg)

                # aid request
                url = f"{BASE_URL}eservices/api/v2/sanadi/aids/subvention-aid"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": response_auth.json().get('rs').get('token')
                }

                request_doc = frappe.get_doc("Beneficiary Request", doc.beneficiary_request)
                aid_lookup_parent_id, aid_lookup_id = get_aid_lookup_parent_id(request_doc)
                doner_id = get_doner_id(doc)
                periodic_type = get_periodic_type(doc.payment_periodicity)

                payment_date = str(doc.payment_date)
                payment_date = datetime.strptime(payment_date, "%Y-%m-%d")
                # Convert the datetime object to the desired format "YYYY-  MM-DDTHH:mm:ssZ"
                payment_date_formatted = payment_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                
                approval_date = str(doc.approval_date)
                approval_date = datetime.strptime(approval_date, "%Y-%m-%d")
                # Convert the datetime object to the desired format "YYYY-MM-DDTHH:mm:ssZ"
                approval_date_formatted = approval_date.strftime("%Y-%m-%dT%H:%M:%SZ")

                body = {
                    "subventionRequestId": int(request_doc.request_id),
                    "aidLookupId": aid_lookup_id,
                    "aidLookupParentId": aid_lookup_parent_id,
                    "donorId": doner_id,
                    "installmentsCount": int(doc.nb_installements),
                    "approvalDate": approval_date_formatted,
                    "periodicType": periodic_type,
                    "aidAmount": float(doc.aid_amount),
                    "aidSuggestedAmount": int(doc.suggested_amount),
                    "aidDescription": doc.disbursement_decision,
                    "aidStartPayDate": payment_date_formatted
                }
                frappe.log_error("body", body)

                response_aid = requests.post(url=url, headers=headers, data=json.dumps(body), verify=False)

                if response_aid.status_code == 200:
                    msg = f"Aid response success: {response_aid.json()}"
                    frappe.log_error("aid response", msg)

                else:
                    msg = f"Aid response fail: {response_aid.json()}"
                    frappe.log_error("aid response", msg)

            else:
                msg = f"Validate response fail: {response_val.json()}"
                frappe.log_error("validate response", msg)

        else:
            msg = f"Authentication response fail: {response_auth.json()}"
            frappe.log_error("authentication response", msg)



def get_doner_id(doc):
    if doc.doner_id == "Donor Entity":
        doner_id = 1
    elif doc.doner_id == "Doner":
        doner_id = 2

    return doner_id


def get_periodic_type(doc):
    if doc == "Monthly":
        periodic_type = 1
    elif doc == "One Time":
        periodic_type = 2

    return periodic_type


def get_income_periodic_type(doc):
    if doc == "Monthly":
        periodic_type = 2
    elif doc == "Yearly":
        periodic_type = 1 
    elif doc == "Others":
        periodic_type = 3

    return periodic_type



def set_committee_member(doc, method):
    frappe.log_error("set_committee_member")
    if len(doc.committee_amount) > 0:
        for amount in doc.committee_amount:
            if amount.suggested_amount and not amount.committee_member:
                amount.committee_member = frappe.session.user
                amount.full_name = frappe.get_value("User", frappe.session.user, "full_name")


def set_approval_date(doc, method):
    frappe.log_error("set_approval_date", doc.workflow_state)
    if doc.workflow_state == "Approved" and not doc.approval_date:
        doc.approval_date = today()


# @frappe.whitelist()
# def get_existing_doc(id):
#     if frappe.db.exists("Beneficiaries Registration", {"ben_primary_idnumber": id}):
#         doc = frappe.get_doc("Beneficiaries Registration", {"ben_primary_idnumber": id})
#         return doc
#     else:
#         return None

@frappe.whitelist()
def get_existing_doc(id, dir):
    if frappe.db.exists("Beneficiaries Registration", {"ben_primary_idnumber": id}):
        user_id = frappe.get_value("Beneficiaries Registration", {"ben_primary_idnumber": id}, "user")

        # split the user_id
        user, domain = user_id.split("@")
        
        # hide the middle part of the user with asterisks
        if len(user) > 2:
            hidden_user = user[0] + "*" * (len(user) - 2) + user[-1]
        else:
            hidden_user = user[0] + "*"
        
        # hide the middle part of the domain with asterisks
        domain_name, domain_extension = domain.split(".")
        if len(domain_name) > 2:
            hidden_domain_name = domain_name[0] + "*" * (len(domain_name) - 2) + domain_name[-1]
        else:
            hidden_domain_name = domain_name[0] + "*"
        

        hidden_user_id = f"{hidden_user}@{hidden_domain_name}.{domain_extension}"
        
        if dir == "rtl":
            msg = f"{id} مرتبط بالفعل بالحساب {hidden_user_id}"
        else:
            msg = f"{id} is already associated with {hidden_user_id}"
        return msg

    else:
        return None



@frappe.whitelist()
def get_full_name(user):
    return frappe.get_value("User", user, "full_name")



# # update User language from language picker
# @frappe.whitelist()
# def update_user_language(user, language):
#     user_doc = frappe.get_doc("User", user)
#     user_doc.language = language
#     user_doc.save()

# @frappe.whitelist()
# def get_user_language(user):
#     user_doc = frappe.get_doc("User", user)
#     language = user_doc.language
#     return language




# scheduler
def expire_documents():
    documents = frappe.get_all('Beneficiary Request', filters={'status': ('!=', 'Expired'), 'declaration': ['=', '']}, fields=['name', 'request_date'])
    for doc in documents:
        submission_date = doc.request_date
        frappe.log_error("submission_date", submission_date)
        expiration_date = add_business_days(submission_date, 3)
        frappe.log_error("expiration_date", expiration_date)
        if now_datetime() >= expiration_date:
            # Update the status to 'Expired' if 3 business days have passed
            expired_doc = frappe.get_doc('Beneficiary Request', doc.name)
            expired_doc.status = 'Expired'
            expired_doc.save()

def add_business_days(start_date, business_days):
    current_date = start_date
    while business_days > 0:
        current_date += timedelta(days=1)
        if current_date.weekday() not in [4, 5]:
            business_days -= 1
    return current_date