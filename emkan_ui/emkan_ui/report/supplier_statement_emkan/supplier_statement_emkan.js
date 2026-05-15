// Copyright (c) 2026, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["Supplier Statement Emkan"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "reqd": 1
        },
        {
            "fieldname": "supplier",
            "label": "Supplier",
            "fieldtype": "Link",
            "options": "Supplier"
        }
    ]
};
