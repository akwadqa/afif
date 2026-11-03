import frappe
from frappe.permissions import setup_custom_perms

# The site's Custom DocPerm rows replace the DocType JSON permissions, so the level-1 access to
# is_account_restricted that the JSON grants is copied to them too.
RESTRICTING_ROLES = ("Supervisor", "System Manager")


def execute():
	setup_custom_perms("Beneficiaries Registration")
	for role in RESTRICTING_ROLES:
		if frappe.db.exists("Custom DocPerm", {"parent": "Beneficiaries Registration", "role": role, "permlevel": 1}):
			continue
		frappe.get_doc(
			{
				"doctype": "Custom DocPerm",
				"parent": "Beneficiaries Registration",
				"parenttype": "DocType",
				"parentfield": "permissions",
				"role": role,
				"permlevel": 1,
				"read": 1,
				"write": 1,
			}
		).insert(ignore_permissions=True)
	frappe.clear_cache(doctype="Beneficiaries Registration")
