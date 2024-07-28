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
			"fieldname": "from", 
			"fieldtype": "Data",
			"width" : 120 
		},
		{
			"label": "Item Code",
			"fieldname": "item_code", 
			"fieldtype": "Link", 
			"options": "Item",
			"width" : 120
		},
		{
			"label": "Item Name",
			"fieldname": "item_name", 
			"fieldtype": "Data",
			"width" : 150 
		},
		{
			"label": "Description",
			"fieldname": "description", 
			"fieldtype": "Data",
			"width" : 300 
		},
		{
			"label": "Qty",
			"fieldname": "qty", 
			"fieldtype": "Int",
			"width" : 70 
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
		{
			"label": "Expense Account",
			"fieldname": "expense_account", 
			"fieldtype": "Data",
			"width" : 150 
		},
	]

	return columns

def get_data(filters):
	data = []
	mr_filters = {}
	
	if filters.get("mr_no"):
		mr_filters["name"] = filters.get("mr_no")

	if filters.get("from") and filters.get("to"):
		mr_filters["transaction_date"] = ["between", [filters.get("from"), filters.get("to")]] 
	
	docs = frappe.get_list("Material Request", mr_filters)
	
	for row in docs:
		doc = frappe.get_doc("Material Request", row.name)
		for mr_item in doc.items:
			data.append({
				"material_request" : doc.name,
				"date" : doc.transaction_date,
				"department": doc.custom_department,
				"from" : doc.custom_from,
				"status" : doc.status,
				"item_code" : mr_item.item_code,
				"item_name" : mr_item.item_name,
				"description" : mr_item.description,
				"qty" : mr_item.qty,
				"remark" : mr_item.custom_remarks,
				"expense_account" : mr_item.expense_account,
			})
			
	return data