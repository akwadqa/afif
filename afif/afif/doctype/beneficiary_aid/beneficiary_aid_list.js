// Copyright (c) 2023, Akwad and contributors
// For license information, please see license.txt

frappe.listview_settings['Beneficiary Aid'] = {
	onload: function (listview) {
		listview.page.add_inner_button(__('Send Bulk SMS'), function () {
			const selected = listview.get_checked_items();

			if (!selected.length) {
				frappe.msgprint(__('Please select at least one row.'));
				return;
			}

			show_bulk_sms_dialog(listview, selected);
		});
	},
};

function show_bulk_sms_dialog(listview, selected_docs) {
	const names = selected_docs.map((d) => d.name);
	const recipient_labels = selected_docs.map((d) => d.beneficiary_name || d.name).join(', ');
	const safe_labels = $('<div>').text(recipient_labels).html();

	const dialog = new frappe.ui.Dialog({
		title: __('Send Bulk SMS ({0} selected)', [selected_docs.length]),
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'recipients_preview',
				options: `<div class="text-muted small" style="margin-bottom: 10px;">
					<b>${__('Recipients')}:</b> ${safe_labels}
				</div>`,
			},
			{
				fieldtype: 'Small Text',
				fieldname: 'message',
				label: __('Message'),
				reqd: 1,
			},
		],
		primary_action_label: __('Send'),
		primary_action(values) {
			frappe.call({
				method: 'afif.afif.doctype.beneficiary_aid.beneficiary_aid.send_bulk_sms',
				args: {
					names: names,
					message: values.message,
				},
				freeze: true,
				freeze_message: __('Sending SMS...'),
				callback: function (r) {
					if (r.message) {
						dialog.hide();
						listview.refresh();
					}
				},
			});
		},
	});

	dialog.show();
}