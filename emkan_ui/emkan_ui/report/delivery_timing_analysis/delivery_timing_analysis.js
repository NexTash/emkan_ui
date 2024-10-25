// Copyright (c) 2024, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["Delivery Timing Analysis"] = {
    "filters": [
        {
            "fieldname": "name",
            "label": __("Material Request ID"),
            "fieldtype": "Link",
            "options": "Material Request"
        },
        {
            "fieldname": "creation",
            "label": __("Creation Date"),
            "fieldtype": "Date"
        },
        {
            "fieldname": "date",
            "label": __("Submission Date"),
            "fieldtype": "Date"
        },
        {
            "label": "Creation to Approval",
            "fieldname": "days_between",
            "fieldtype": "Int"
        }
    ]
}
