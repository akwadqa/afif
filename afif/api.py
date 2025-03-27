import frappe

def update_suggested_amount():
    aids = frappe.get_all(
        "Beneficiary Aid",
        filters={"approval_date": (">=", "2025-01-01")},
        fields=["name", "aid_amount"]
    )
    frappe.log_error("AIDS", aids)
    for aid in aids:
        doc = frappe.get_doc("Beneficiary Aid", aid.name)
        doc.suggested_amount = int(float(doc.aid_amount))
        doc.save(ignore_permissions=True)