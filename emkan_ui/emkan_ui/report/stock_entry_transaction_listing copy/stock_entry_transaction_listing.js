// Copyright (c) 2025, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["Stock Entry Transaction Listing"] = {
	"filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_days(frappe.datetime.get_today(), -30),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "purpose",
            "label": __("Purpose"),
            "fieldtype": "Select",
            "options": [
                "",
                "Material Issue",
                "Material Receipt",
                "Material Transfer",
                "Manufacture",
                "Repack",
                "Subcontract"
            ]
        }
    ]
};
