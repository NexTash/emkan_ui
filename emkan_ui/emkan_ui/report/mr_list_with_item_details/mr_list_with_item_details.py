# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": "MR No",
			"fieldname": "material_request", 
			"fieldtype": "Link", 
			"options": "Material Request",
			"width" : 200
		},
		{
			"label": "Date",
			"fieldname": "date", 
			"fieldtype": "Date",
			"width" : 120 
		},
		{
			"label": "Department",
			"fieldname": "department", 
			"fieldtype": "Data",
			"width" : 120 
		},
		{
			"label": "From",
			"fieldname": "purpose", 
			"fieldtype": "Data",
			"width" : 120 
		},
		{
			"label": "Code",
			"fieldname": "item_code", 
			"fieldtype": "Link", 
			"options": "Item",
			"width" : 120
		},
		{
			"label": "Name",
			"fieldname": "item_name", 
			"fieldtype": "Data",
			"width" : 120 
		},
		{
			"label": "Qty",
			"fieldname": "qty", 
			"fieldtype": "Int",
			"width" : 120 
		},
		{
			"label": "Remark",
			"fieldname": "remark", 
			"fieldtype": "Data",
			"width" : 120 
		},
		{
			"label": "Status",
			"fieldname": "status", 
			"fieldtype": "Data",
			"width" : 120 
		},
	]

	return columns

def get_data(filters):
	data = []
	my_filters = {}
	if filters.get("from") and filters.get("to"):
		my_filters["transaction_date"] = ["between", [filters.get("from"), filters.get("to")]] 
	mr_docs = frappe.get_list("Material Request",my_filters, ['name'])
	for row in mr_docs:
		doc = frappe.get_doc("Material Request", row.name)
		for item in doc.items:
			data.append({
				"material_request" : doc.name,
				"date" : doc.transaction_date,
				"department": doc.custom_department,
				"purpose" : doc.custom_from,
				"item_code" : item.item_code,
				"item_name" : item.item_name,
				"qty" : item.qty,
				"remark" : item.custom_remarks,
				"status" : doc.status,



			})
	return data