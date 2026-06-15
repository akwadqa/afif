// Copyright (c) 2025, Akwad and contributors
// For license information, please see license.txt

frappe.ui.form.on('Beneficiaries Registration', {
	refresh: function (frm) {
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

		if (!frm.doc.update_required) {
			frm.add_custom_button('Update Required', function () {
				frappe.call({
					method: 'afif.hooks_call.beneficiary_update_required_status_for_document',
					args: {
						beneficiary_name: frm.doc.name
					},
					callback: function (r) {
						if (!r.exc) {
							frappe.msgprint(r.message || 'Beneficiary status updated successfully.');
							frm.reload_doc(); // refresh form to show updated status
						}
					}
				});
			});
		}
	}
});