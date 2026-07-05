import frappe


def execute():
	rows = frappe.db.sql(
		"""
		SELECT name, additional_documents
		FROM `tabBeneficiaries Registration`
		WHERE additional_documents IS NOT NULL AND additional_documents != ''
		""",
		as_dict=True,
	)

	for row in rows:
		already_migrated = frappe.db.exists(
			"Beneficiary Additional Document",
			{
				"parent": row.name,
				"parenttype": "Beneficiaries Registration",
				"parentfield": "additional_attachments",
				"attachment": row.additional_documents,
			},
		)
		if already_migrated:
			continue

		next_idx = frappe.db.count(
			"Beneficiary Additional Document",
			{
				"parent": row.name,
				"parenttype": "Beneficiaries Registration",
				"parentfield": "additional_attachments",
			},
		) + 1

		child = frappe.new_doc("Beneficiary Additional Document")
		child.parent = row.name
		child.parenttype = "Beneficiaries Registration"
		child.parentfield = "additional_attachments"
		child.idx = next_idx
		child.attachment = row.additional_documents
		child.insert(ignore_permissions=True)

	frappe.db.commit()
