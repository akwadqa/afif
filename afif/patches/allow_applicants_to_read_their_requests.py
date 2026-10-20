import frappe
from frappe.permissions import setup_custom_perms

# A scholarship request is created with the registration, so the applicant has a request before
# being accepted, and keeps it if the registration is rejected (spec/scholarship_flow, Phase 7).
APPLICANT_ROLES = ("Beneficiary New Registration", "Beneficiary Not Accepted")


def execute():
	setup_custom_perms("Beneficiary Request")
	for role in APPLICANT_ROLES:
		if frappe.db.exists("Custom DocPerm", {"parent": "Beneficiary Request", "role": role, "permlevel": 0}):
			continue
		frappe.get_doc(
			{
				"doctype": "Custom DocPerm",
				"parent": "Beneficiary Request",
				"parenttype": "DocType",
				"parentfield": "permissions",
				"role": role,
				"permlevel": 0,
				"read": 1,
				"if_owner": 1,
			}
		).insert(ignore_permissions=True)
	frappe.clear_cache(doctype="Beneficiary Request")
