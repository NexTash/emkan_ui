// Copyright (c) 2024, NexTash and contributors
// For license information, please see license.txt

frappe.query_reports["Asset Builder"] = {
	"filters": [
		{
			fieldname: "asset",
			label: __("Asset"),
			fieldtype: "Link",
			options: "Asset",
			// reqd: 1,
		},
		{
			fieldname: "location",
			label: __("Location"),
			fieldtype: "Link",
			options: "Location",
			// reqd: 1,
		},
		{
			fieldname: "item_code",
			label: __("Item Code"),
			fieldtype: "Link",
			options: "Item",
			// reqd: 1,
		},
		
	]
};
