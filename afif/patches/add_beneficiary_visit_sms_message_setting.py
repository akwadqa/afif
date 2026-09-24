import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"SMS Settings": [
				{
					"fieldname": "visit_sms_message",
					"fieldtype": "Small Text",
					"label": "Beneficiary Visit SMS Message",
					"insert_after": "use_post",
					"default": "يرجى الحضور لمؤسسة عفيف للمراجعة غداً من الساعه 10ص-12م",
					"description": "Message sent to a beneficiary via the \"Send SMS\" button on the Beneficiary Request form.",
				}
			]
		},
		update=True,
	)

	frappe.db.set_single_value(
		"SMS Settings",
		"visit_sms_message",
		"يرجى الحضور لمؤسسة عفيف للمراجعة غداً من الساعه 10ص-12م",
	)
