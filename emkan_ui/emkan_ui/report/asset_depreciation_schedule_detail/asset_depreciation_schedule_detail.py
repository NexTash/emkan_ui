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
	docs = frappe.get_list("Asset", asset_filters, ["*"])

	# Convert from_date and to_date from string to date objects
	from_date = getdate(filters.get("from_date")) if filters.get("from_date") else None
	to_date = getdate(filters.get("to_date")) if filters.get("to_date") else None

	for row in docs:
		child_filters = {"asset": row.name}

		# Fetch depreciation schedules
		dep_docs = frappe.get_list("Asset Depreciation Schedule", child_filters, ["name"])

		for child in dep_docs:
			doc = frappe.get_doc("Asset Depreciation Schedule", child.name)

			# Apply the From Date and To Date filter on schedule_date
			for child1 in doc.depreciation_schedule:
				schedule_date = getdate(child1.schedule_date)

				# Skip rows outside the date range
				if from_date and to_date:
					if not (from_date <= schedule_date <= to_date):
						continue

				je = "No"
				if child1.journal_entry:
					je = "Yes"

				data.append({
					"asset": row.name,
					"item_code": row.item_code,
					"asset_name": row.asset_name,
					"location": row.location,
					"schedule_date": child1.schedule_date,
					"depreciation_amount": child1.depreciation_amount,
					"accumulated_depreciation_amount": child1.accumulated_depreciation_amount,
					"journal_entry": je,
					"journal_number": child1.journal_entry,
				})

	return data
