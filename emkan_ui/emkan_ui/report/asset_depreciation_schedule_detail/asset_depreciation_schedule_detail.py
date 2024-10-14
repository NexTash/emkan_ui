import frappe
from frappe.utils import getdate

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

	# Apply asset, location, and item_code filters if provided
	if filters.get("asset"):
		asset_filters["name"] = filters.get("asset")
	if filters.get("location"):
		asset_filters["location"] = filters.get("location")
	if filters.get("item_code"):
		asset_filters["item_code"] = filters.get("item_code")

	# Fetch Asset records based on filters
	docs = frappe.get_all("Asset", asset_filters, ["name", "item_code", "asset_name", "location"])

	# Convert from_date and to_date from string to date objects
	from_date = getdate(filters.get("from_date")) if filters.get("from_date") else None
	to_date = getdate(filters.get("to_date")) if filters.get("to_date") else None

	# Apply date range filter if both from_date and to_date are provided
	for row in docs:
		child_filters = {"custom_asset": row.name}

		# Apply the date filter directly to depreciation schedules
		if from_date and to_date:
			child_filters["schedule_date"] = ["between", [from_date, to_date]]

		# Fetch filtered depreciation schedules based on the asset and date range
		dep_docs = frappe.get_all("Depreciation Schedule", filters=child_filters, fields=["*"])
		for child in dep_docs:
			je = "No"
			if child.journal_entry:
				je = "Yes"

			# Append data to the list
			data.append({
				"asset": row.name,
				"item_code": row.item_code,
				"asset_name": row.asset_name,
				"location": row.location,
				"schedule_date": child.schedule_date,
				"depreciation_amount": child.depreciation_amount,
				"accumulated_depreciation_amount": child.accumulated_depreciation_amount,
				"journal_entry": je,
				"journal_number": child.journal_entry,
			})

	return data