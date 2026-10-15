// Copyright (c) 2026, Akwad and contributors
// For license information, please see license.txt

// No top-level const/let: Frappe can evaluate this script more than once per page,
// and redeclaring a global const throws and leaves the report blank.
frappe.query_reports["Donation Report"] = {
	status_colors: { Paid: "green", Pending: "orange", Failed: "red" },

	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "date_based_on",
			label: __("Date Based On"),
			fieldtype: "Select",
			options: [
				{ value: "Created On", label: __("Created On") },
				{ value: "Paid At", label: __("Paid At") },
			],
			default: "Created On",
		},
		{
			fieldname: "payment_status",
			label: __("Payment Status"),
			fieldtype: "Select",
			options: ["", "Pending", "Paid", "Failed"],
		},
		{
			fieldname: "donation_program",
			label: __("Program"),
			fieldtype: "Link",
			options: "Donation Program",
		},
		{
			fieldname: "donation_project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Donation Project",
			get_query: () => {
				const program = frappe.query_report.get_filter_value("donation_program");
				return program ? { filters: { program } } : {};
			},
		},
		{
			fieldname: "donation_frequency",
			label: __("Frequency"),
			fieldtype: "Select",
			options: ["", "One-Time", "Daily", "Monthly", "Annual"],
		},
		{
			fieldname: "currency",
			label: __("Currency"),
			fieldtype: "Link",
			options: "Currency",
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: [
				{ value: "None", label: __("None") },
				{ value: "Program", label: __("Program") },
				{ value: "Project", label: __("Project") },
				{ value: "Program > Project", label: __("Program > Project") },
			],
			default: "None",
		},
		{
			fieldname: "is_anonymous",
			label: __("Benefactor"),
			fieldtype: "Select",
			options: [
				{ value: "", label: "" },
				{ value: "Yes", label: __("Yes") },
				{ value: "No", label: __("No") },
			],
		},
		{ fieldname: "donor_name", label: __("Donor Name"), fieldtype: "Data" },
		{ fieldname: "donor_mobile", label: __("Donor Mobile"), fieldtype: "Data" },
		{ fieldname: "donor_email", label: __("Donor Email"), fieldtype: "Data" },
		{ fieldname: "reference_id", label: __("Reference ID"), fieldtype: "Data" },
		{ fieldname: "gateway_transaction_id", label: __("Gateway Txn ID"), fieldtype: "Data" },
	],

	// When grouped, rows nest under group headers; tree mode makes the total row sum only top-level headers
	get tree() {
		const group_by = frappe.query_report?.get_filter_value("group_by");
		return Boolean(group_by && group_by !== "None");
	},
	parent_field: "parent_group",

	formatter(value, row, column, data, default_formatter) {
		if (data?.is_group && column.fieldname === "name") {
			const title = frappe.utils.escape_html(value || "");
			return data.group_id
				? `<a href="/app/${frappe.router.slug(data.group_doctype)}/${encodeURIComponent(data.group_id)}"><b>${title}</b></a>`
				: `<b>${title}</b>`;
		}

		value = default_formatter(value, row, column, data);
		if (!data) return value;

		if (data.is_group && column.fieldname === "amount") {
			return `<b>${value}</b>`;
		}
		const status_color = frappe.query_reports["Donation Report"].status_colors[data.payment_status];
		if (column.fieldname === "payment_status" && status_color) {
			return `<span class="indicator-pill ${status_color}">${value}</span>`;
		}

		const link = {
			program_title: ["donation-program", data.program],
			project_title: ["donation-project", data.project],
		}[column.fieldname];
		if (link?.[1]) {
			return `<a href="/app/${link[0]}/${encodeURIComponent(link[1])}">${value}</a>`;
		}
		return value;
	},
};
