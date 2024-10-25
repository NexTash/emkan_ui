# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, date_diff

def execute(filters=None):
    
    columns = [
        {
            "label": "Material Request ID",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Material Request"
        },
        {
            "label": "Creation Date",
            "fieldname": "creation",
            "fieldtype": "Date"
        },
        {
            "label": "Submission Date",
            "fieldname": "date",
            "fieldtype": "Date"
        },
        {
            "label": "Creation to Approval",
            "fieldname": "days_between",
            "fieldtype": "Int"
        },
        {
            "label": "PO Creation Time",
            "fieldname": "po_creation_date",
            "fieldtype": "Time"
        },
        {
            "label": "MR to PO Days",
            "fieldname": "mr_to_po_days",
            "fieldtype": "Int"
        },
        {
            "label": "PR Creation Time",
            "fieldname": "pr_creation_date",
            "fieldtype": "Time"
        },
        {
            "label": "PO to PR Days",
            "fieldname": "po_to_pr_days",
            "fieldtype": "Int"
        }
    ]
    
    data = []
    mr_filters = {}


    if filters.get("creation"):
        mr_filters["creation"] = [">", filters.get("creation")]

    if filters.get("name"):
        mr_filters["name"] = filters.get("name")
    
    if filters.get("date"):
        mr_filters["date"] = [">", filters.get("date")]
        
    if filters.get("days_between"):
        mr_filters["days_between"] = [">", filters.get("days_between")]


    material_requests = frappe.get_all(
        "Material Request",
        fields=[
            "name",
            "creation",
        ],
        filters=mr_filters if mr_filters else {}, 
    )
    
    
    for request in material_requests:
        
        material_request_doc = frappe.get_doc("Material Request", request.name)
        coo_approved_date = None
        verification_or_prepared_date = None
        days_between = None
        pr_creation_date = None
        po_to_pr_days = None
        mr_to_po_days = None

        for doc in material_request_doc.custom_workflow_status: 
          
              if doc.workflow_states == "COO Approved":
                coo_approved_date = getdate(doc.date).strftime("%Y-%m-%d") if doc.date else None
              if doc.workflow_states in ["MR Prepared", "Store Verification"]:
                verification_or_prepared_date = getdate(doc.date).strftime("%Y-%m-%d") if doc.date else None
    
        if coo_approved_date and verification_or_prepared_date:
            days_between = date_diff(coo_approved_date, verification_or_prepared_date)

        # Fetch Purchase Order creation date
        po_creation_date = None
        po_list = frappe.get_all(
            "Purchase Order Item",
            filters={"material_request": request.name},
            fields=["parent"]
        )
            
        if po_list:
            # Fetch the first related Purchase Order and get its creation date
            po_doc = frappe.get_doc("Purchase Order",  po_list[0].parent)
            po_creation_date = getdate(po_doc.creation).strftime("%Y-%m-%d") if po_doc.creation else None
            mr_to_po_days = date_diff(po_doc.creation, request.creation)
            
            pr_list = frappe.get_all(
                "Purchase Receipt Item",
                filters={"purchase_order": po_doc.name},
                fields=["parent"]
            )
            
            if pr_list:
                pr_doc = frappe.get_doc("Purchase Receipt", pr_list[0].parent)
                pr_creation_date = getdate(pr_doc.creation).strftime("%Y-%m-%d") if pr_doc.creation else None
                po_to_pr_days = date_diff(pr_doc.creation, po_doc.creation)
                
        data.append({
            "name": request.name,
            "creation": getdate(request.creation).strftime("%Y-%m-%d"), 
            "transaction_date": getdate(request.transaction_date).strftime("%Y-%m-%d") if request.transaction_date else None, 
            "schedule_date": getdate(request.schedule_date).strftime("%Y-%m-%d") if request.schedule_date else None,
            "date": coo_approved_date,
            "days_between": days_between,
            "po_creation_date": po_creation_date,
            "pr_creation_date": pr_creation_date,
            "po_to_pr_days": po_to_pr_days,
            "mr_to_po_days": mr_to_po_days                             
        })
    
    return columns, data


