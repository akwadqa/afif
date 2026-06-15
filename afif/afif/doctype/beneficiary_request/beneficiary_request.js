// Copyright (c) 2023, Akwad and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beneficiary Request', {
	refresh(frm) {
		if (!frm.is_new()) {
			let $print = frm.add_custom_button(__('Print'), function () {
				frm.print_doc();
			});
			$print.html(frappe.utils.icon('printer', 'sm') + ' ' + __('Print'));

			if (cint(frm.doc.docstatus) != 1 && frappe.model.can_delete(frm.doctype)) {
				frm.add_custom_button(__('Delete'), function () {
					frm.savetrash();
				});
			}
		}
	},

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
