// Copyright (c) 2025, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["Profit & Loss by Grouped & Summarized Project"] = {
	filters: [
		{
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1,
            "default": frappe.defaults.get_default("Company")
        },
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start()
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_end()
		}
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
	
		if (column.fieldname === "label" && data.indent === 2 && data.account) {
			const route_options = {
				account: data.account,
				from_date: frappe.query_report.get_filter_value("from_date"),
				to_date: frappe.query_report.get_filter_value("to_date"),
				project: data.project,
				group_by: "Group by Project"
			};
	
			const options_string = JSON.stringify(route_options).replace(/"/g, '&quot;');
			return `<span  onclick='frappe.set_route("query-report", "General Ledger For Profit & Loss", ${options_string})'>${value}</span>`;
		}
	
		return value;
	}
	
	
	
};
