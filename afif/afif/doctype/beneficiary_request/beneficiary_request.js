// Copyright (c) 2023, Akwad and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beneficiary Request', {
	before_workflow_action(frm) {
		if (frm.selected_workflow_action !== "Approve") return;
		return new Promise((resolve, reject) => {
			frappe.call({
				method: "check_beneficiary_id",
				doc: frm.doc,
				callback(r) {
					if (!r.message || r.message.success !== true) {
						frappe.msgprint({
							title: __('Cannot Approve'),
							message: r.message?.message || __('Validation failed'),
							indicator: 'red'
						});
						reject(); // stops workflow action
						frappe.dom.unfreeze();
						return;
					}

					resolve();
				},
				error() {					
					reject();
				}
			});
		});
	}
});
