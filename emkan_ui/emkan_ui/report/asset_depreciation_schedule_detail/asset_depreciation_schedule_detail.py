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

    # Convert from_date and to_date from string to date objects
    from_date = getdate(filters.get("from_date")) if filters.get("from_date") else None
    to_date = getdate(filters.get("to_date")) if filters.get("to_date") else None

    # Ensure both from_date and to_date are valid
    if from_date and to_date and from_date > to_date:
        frappe.throw("From Date cannot be greater than To Date")

    # Apply asset, location, and item_code filters if provided
    asset_filters = {}
    if filters.get("asset"):
        asset_filters["name"] = filters.get("asset")
    if filters.get("location"):
        asset_filters["location"] = filters.get("location")
    if filters.get("item_code"):
        asset_filters["item_code"] = filters.get("item_code")

    # Fetch asset names that match the filters
    assets = frappe.get_list("Asset", filters=asset_filters, fields=["name"])
    asset_names = [asset.name for asset in assets]

    if not asset_names:
        return data

    # SQL Query to fetch the required data with joins
    query = """
        SELECT
            ds.schedule_date,
            ds.depreciation_amount,
            ds.accumulated_depreciation_amount,
            ds.journal_entry,
            fa.name AS asset,
            fa.item_code,
            fa.asset_name,
            fa.location
        FROM
            `tabDepreciation Schedule` ds
        INNER JOIN
            `tabAsset Depreciation Schedule` ads ON ds.parent = ads.name
        INNER JOIN
            `tabAsset` fa ON ads.asset = fa.name
        WHERE
            ds.schedule_date BETWEEN %(from_date)s AND %(to_date)s
            AND fa.name IN %(asset_names)s
    """

    # Execute the query using Frappe's db.sql
    results = frappe.db.sql(query, {
        "from_date": from_date,
        "to_date": to_date,
        "asset_names": tuple(asset_names)
    }, as_dict=True)

    # Process the results and prepare the data for output
    for row in results:
        je = "Yes" if row.journal_entry else "No"
        data.append({
            "asset": row.asset,
            "item_code": row.item_code,
            "asset_name": row.asset_name,
            "location": row.location,
            "schedule_date": row.schedule_date,
            "depreciation_amount": row.depreciation_amount,
            "accumulated_depreciation_amount": row.accumulated_depreciation_amount,
            "journal_entry": je,
            "journal_number": row.journal_entry
        })

    return data
