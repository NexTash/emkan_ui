# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_columns(filters):
	columns = [
		{
			"label": "Asset",
			"fieldname": "asset", 
			"fieldtype": "Link", 
			"options": "Asset",
		},
		{
			"label": "Asset Name",
			"fieldname": "asset_name", 
			"fieldtype": "Data",
			# "width" : 120 
		},
		{
			"label": "Item Code",
			"fieldname": "item_code", 
			"fieldtype": "Link", 
			"options": "Item",
		},
		{
			"label": "Location",
			"fieldname": "location", 
			"fieldtype": "Link", 
			"options": "Location",
		},
		{
			"label": "Schedule Date",
			"fieldname": "schedule_date", 
			"fieldtype": "Date", 
		},
		{
			"label": "Depreciation Amount",
			"fieldname": "depreciation_amount", 
			"fieldtype": "Currency", 
		},
		{
			"label": "Accumulated Depreciation Amount",
			"fieldname": "accumulated_depreciation_amount", 
			"fieldtype": "Currency", 
		},
		{
			"label": "Journal Entry",
			"fieldname": "journal_entry", 
			"fieldtype": "Data", 
		},
		{
			"label": "Journal Number",
			"fieldname": "journal_number", 
			"fieldtype": "Link", 
			"options": "Journal Entry", 
		},
	]

	return columns

def get_data(filters):
	data = []
	asset_filters = {}
	if filters.get("asset"):
		asset_filters["name"] = filters.get("asset")
	if filters.get("location"):
		asset_filters["location"] = filters.get("location")
	if filters.get("item_code"):
		asset_filters["item_code"] = filters.get("item_code")
	docs = frappe.get_list("Asset",asset_filters, ["*"])
	for row in docs:
		child_filters = {"asset" : row.name}
		dep_docs = frappe.get_list("Asset Depreciation Schedule", child_filters, ["name"])
		for child in dep_docs:
			doc = frappe.get_doc("Asset Depreciation Schedule", child.name)
			for child1 in doc.depreciation_schedule:
				je = "No"
				if child1.journal_entry:
					je = "Yes"
				data.append({
					"asset" : row.name,
					"item_code": row.item_code,
					"asset_name" : row.asset_name,
					"location" : row.location,
					"schedule_date" : child1.schedule_date,
					"depreciation_amount" : child1.depreciation_amount,
					"accumulated_depreciation_amount" : child1.accumulated_depreciation_amount,
					"journal_entry" : je,
                    "journal_number" : child1.journal_entry,
				})
			
	return data