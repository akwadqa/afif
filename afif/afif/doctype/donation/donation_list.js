// Copyright (c) 2026, Akwad and contributors
// For license information, please see license.txt

const DONATION_REPORT_EXACT_FILTERS = [
	"payment_status",
	"donation_program",
	"donation_project",
	"donation_frequency",
	"currency",
];
const DONATION_REPORT_TEXT_FILTERS = [
	"donor_name",
	"donor_mobile",
	"donor_email",
	"reference_id",
	"gateway_transaction_id",
];

frappe.listview_settings["Donation"] = {
	onload(listview) {
		listview.page.add_inner_button(__("Donation Report"), () => {
			// Carry the list's current filters over to the report where they map cleanly
			const route_options = {};
			for (const [, field, operator, value] of listview.get_filters_for_args()) {
				if (operator === "=" && DONATION_REPORT_EXACT_FILTERS.includes(field)) {
					route_options[field] = value;
				} else if (operator === "like" && DONATION_REPORT_TEXT_FILTERS.includes(field)) {
					route_options[field] = String(value).replace(/^%|%$/g, "");
				}
			}
			frappe.route_options = route_options;
			frappe.set_route("query-report", "Donation Report");
		});
	},
};
