// Copyright (c) 2025, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["Project-wise Report"] = {
    "filters": [
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
            width: 100,
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            on_change: function(report) {
                let from_date = frappe.query_report.get_filter_value('from_date');
                localStorage.setItem("from_date", JSON.stringify({ from_date: from_date || null }));
                report.refresh();
            }
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            width: 100,
            default: frappe.datetime.get_today(),
            on_change: function(report) {
                let to_date = frappe.query_report.get_filter_value('to_date');
                localStorage.setItem("to_date", JSON.stringify({ to_date: to_date || null }));
                report.refresh();
            }
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "reqd": 0
        }
    ]
};
