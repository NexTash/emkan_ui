// Copyright (c) 2024, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["Delivery Timing Analysis"] = {
	"filters": [
		{
            "fieldname": "material_request_id",
            "label": __("Material Request ID"),
            "fieldtype": "Link",
            "options": "Material Request",
            "reqd": 0
        },
        {
            "fieldname": "creation_date",
            "label": __("Creation Date"),
            "fieldtype": "Date",
            "reqd": 0
        }
	]
};
