// Copyright (c) 2024, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["MR List with Item Details"] = {
	"filters": [
		{
			"label": "From Date",
			"fieldname": "from", 
			"fieldtype": "Date", 
		},
		{
			"label": "To Date",
			"fieldname": "to", 
			"fieldtype": "Date", 
		},
		{
			"label": "Material Request",
			"fieldname": "mr_no", 
			"fieldtype": "Link",
			"options": "Material Request",
		},
	]
};
