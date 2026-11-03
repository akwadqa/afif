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

		if (frm.doc.phone_number) {
			let $whatsapp = frm.add_custom_button(__('WhatsApp'), function () {
				let digits = (frm.doc.phone_number || '').replace(/\D/g, '');
				if (!digits.startsWith('974')) {
					digits = '974' + digits;
				}
				window.open('https://wa.me/' + digits, '_blank');
			});
			$whatsapp.html(frappe.utils.icon('message', 'sm') + ' ' + __('WhatsApp'));
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

		if (!frm.is_new() && frm.doc.is_scholarship && frm.perm[1] && frm.perm[1].write) {
			const is_restricted = cint(frm.doc.is_account_restricted);
			const label = is_restricted ? __('Lift Account Restriction') : __('Restrict Account');
			const confirmation = is_restricted
				? __('Lift the restriction? The student will be able to file new requests again.')
				: __('Restrict this account because the scholarship has ended? The student will no longer be able to file new requests.');

			// The form's Save would require the registration documents, which a scholarship student
			// may still owe after "Update Required", so the restriction is set through its own call.
			frm.add_custom_button(label, function () {
				frappe.confirm(confirmation, function () {
					frappe.call({
						method: 'afif.afif.doctype.beneficiaries_registration.beneficiaries_registration.set_account_restriction',
						args: {
							registration: frm.doc.name,
							is_restricted: is_restricted ? 0 : 1
						},
						freeze: true,
						callback: function (r) {
							if (!r.exc) {
								frm.reload_doc();
							}
						}
					});
				});
			});
		}

		if (!frm.is_new() && frappe.user_roles.some(role => ['System Manager', 'Supervisor', 'Specialist'].includes(role))) {
			frm.add_custom_button(__('Change Linked Account'), function () {
				frappe.prompt(
					[
						{
							fieldname: 'new_email',
							label: __('New Email'),
							fieldtype: 'Data',
							options: 'Email',
							reqd: 1,
							description: __('The beneficiary will use this email to log in going forward.')
						}
					],
					function (values) {
						frappe.confirm(
							__('Re-link this beneficiary to {0}? The current account ({1}) will lose access.', [values.new_email, frm.doc.user]),
							function () {
								frappe.call({
									method: 'afif.hooks_call.change_beneficiary_linked_account',
									args: {
										beneficiary_name: frm.doc.name,
										new_email: values.new_email
									},
									freeze: true,
									callback: function (r) {
										if (!r.exc) {
											const message = r.message && r.message.message ? r.message.message : __('Linked account updated.');
											// Show the dialog only after the reload: this callback runs before
											// frappe.request.cleanup(), which calls hide_msgprint() whenever the
											// response carries server messages — that empties an already-open
											// msgprint dialog and leaves it on screen with no content.
											frm.reload_doc().then(() => {
												frappe.msgprint({
													title: __('Change Linked Account'),
													indicator: 'green',
													message: message
												});
											});
										}
									}
								});
							}
						);
					},
					__('Change Linked Account'),
					__('Update')
				);
			});
		}
	}
});