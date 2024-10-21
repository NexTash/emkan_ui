# # Copyright (c) 2024, NexTash and contributors
# # For license information, please see license.txt

import frappe
from frappe.utils import getdate

def execute(filters=None):
    # Define the report columns
    columns = [
        {
            "label": "Material Request ID",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Material Request",
            # "width": 150
        },
        {
            "label": "Creation Date",
            "fieldname": "creation",
            "fieldtype": "Date",
            # "width": 150
        },
        {
            "label": "Transaction Date",
            "fieldname": "transaction_date",
            "fieldtype": "Date",
            # "width": 150
        },
        {
            "label": "Schedule Date",
            "fieldname": "schedule_date",
            "fieldtype": "Date",
            # "width": 150
        },
        {
            "label": "Delayed",
            "fieldname": "is_delayed",
            "fieldtype": "Check",
            # "width": 100
        }
    ]
    
    # Fetching material requests with required fields
    material_requests = frappe.get_list(
        "Material Request",
        fields=[
            "name",                # Document name or ID
            "creation",            # Creation timestamp
            "transaction_date",    # Transaction date
            "schedule_date"        # Schedule date
        ],
        filters={},
        order_by="creation desc"  # Sort by creation date, latest first
    )
    
    # Prepare data for the report
    data = []
    for request in material_requests:
        # Determine if the request is delayed
        is_delayed = getdate(request.transaction_date) > getdate(request.schedule_date)

        data.append({
            "name": request.name,                                           # Material Request ID
            "creation": getdate(request.creation).strftime("%Y-%m-%d"),  # Format creation date
            "transaction_date": getdate(request.transaction_date).strftime("%Y-%m-%d") if request.transaction_date else None,  # Format transaction date
            "schedule_date": getdate(request.schedule_date).strftime("%Y-%m-%d") if request.schedule_date else None,  # Format schedule date
            "is_delayed": is_delayed                                       # Flag for delayed requests
        })
    
    return columns, data

