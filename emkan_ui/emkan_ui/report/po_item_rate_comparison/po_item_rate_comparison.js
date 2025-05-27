// Copyright (c) 2025, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["PO Item Rate Comparison"] = {
    "filters": [
        {
            "fieldname": "po_number",
            "label": "Purchase Order",
            "fieldtype": "Link",
            "options": "Purchase Order",
            "reqd": 1
        },
        {
            "fieldname": "current_date",
            "label": "Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "hidden": 1
        }
    ]
};
