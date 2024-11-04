# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import get_datetime, date_diff

def execute(filters=None):
    columns = [
        {
            "label": "Material Request ID",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Material Request",
        },
        {
            "label": "Creation Date",
            "fieldname": "creation",
            "fieldtype": "Date",
        },
        {
            "label": "Submission Date",
            "fieldname": "submission_date",
            "fieldtype": "Date",
        },
        {
            "label": "Creation to Approval",
            "fieldname": "days_between",
            "fieldtype": "Int",
        },
        {
            "label": "PO Creation Date",
            "fieldname": "po_creation_date",
            "fieldtype": "Datetime",
        },
        {
            "label": "MR to PO Days",
            "fieldname": "mr_to_po_days",
            "fieldtype": "Int",
        },
        {
            "label": "PR Creation Time",
            "fieldname": "pr_creation_date",
            "fieldtype": "Datetime",
        },
        {
            "label": "PO to PR Days",
            "fieldname": "po_to_pr_days",
            "fieldtype": "Int",
        }
    ]

    data = []

    # Filter conditions
    mr_filters = {}
    if filters.get("creation"):
        mr_filters["creation"] = [">", filters.get("creation")]
    if filters.get("name"):
        mr_filters["name"] = filters.get("name")

    material_requests = frappe.get_all(
        "Material Request",
        fields=["name", "creation"],
        filters=mr_filters if mr_filters else {}
    )

    for request in material_requests:
        material_request_doc = frappe.get_doc("Material Request", request.name)
        submission_date = None
        for status in material_request_doc.custom_workflow_status:
            if status.workflow_states == "COO Approved":
                submission_date = status.date
                break
        
        days_between = None
        po_creation_date = None
        mr_to_po_days = None
        pr_creation_date = None
        po_to_pr_days = None

        if submission_date:
            days_between = date_diff(submission_date, request.creation)

        # Fetch Purchase Order creation date
        po_list = frappe.get_all(
            "Purchase Order Item",
            filters={"material_request": request.name},
            fields=["parent"]
        )
        if po_list:
            po_doc = frappe.get_doc("Purchase Order", po_list[0].parent)
            po_creation_date = get_datetime(po_doc.creation).strftime("%Y-%m-%d %H:%M:%S")
            mr_to_po_days = date_diff(po_doc.creation, submission_date)

            # Fetch Purchase Receipt creation date
            pr_list = frappe.get_all(
                "Purchase Receipt Item",
                filters={"purchase_order": po_doc.name},
                fields=["parent"]
            )
            if pr_list:
                pr_doc = frappe.get_doc("Purchase Receipt", pr_list[0].parent)
                pr_creation_date = get_datetime(pr_doc.creation).strftime("%Y-%m-%d %H:%M:%S")
                po_to_pr_days = date_diff(pr_doc.creation, po_doc.creation)
        else:
            # Handle cases where no Purchase Order is found
            po_creation_date = None
            mr_to_po_days = None

        data.append({
            "name": request.name,
            "creation": request.creation.strftime("%Y-%m-%d %H:%M:%S"),
            "submission_date": submission_date.strftime("%Y-%m-%d %H:%M:%S") if submission_date else None,
            "days_between": days_between,
            "po_creation_date": po_creation_date,
            "mr_to_po_days": mr_to_po_days,
            "pr_creation_date": pr_creation_date,
            "po_to_pr_days": po_to_pr_days
        })

    return columns, data
