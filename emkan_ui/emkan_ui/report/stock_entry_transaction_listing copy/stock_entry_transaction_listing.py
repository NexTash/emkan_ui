# Copyright (c) 2025, NexTash and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Stock Entry", "fieldname": "stock_entry", "fieldtype": "Link", "options": "Stock Entry", "width": 150},
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
        {"label": "Posting Time", "fieldname": "posting_time", "fieldtype": "Time", "width": 100},
        {"label": "Purpose", "fieldname": "purpose", "fieldtype": "Data", "width": 120},
        {"label": "Document Status", "fieldname": "document_status", "fieldtype": "Data", "width": 100},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Float", "width": 100},
        {"label": "UOM", "fieldname": "uom", "fieldtype": "Data", "width": 80},
        {"label": "Unit Rate", "fieldname": "unit_rate", "fieldtype": "Currency", "width": 120},
        {"label": "Total Cost", "fieldname": "total_cost", "fieldtype": "Currency", "width": 120},
        {"label": "Source Warehouse", "fieldname": "source_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": "Target Warehouse", "fieldname": "target_warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": "Cost Center", "fieldname": "cost_center", "fieldtype": "Link", "options": "Cost Center", "width": 150},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": "GL Account", "fieldname": "gl_account", "fieldtype": "Link", "options": "Account", "width": 150},
        {"label": "Created By", "fieldname": "created_by", "fieldtype": "Link", "options": "User", "width": 150}
    ]

def get_data(filters):
    conditions = []
    values = {}

    if filters.get("from_date") and filters.get("to_date"):
        conditions.append("se.posting_date BETWEEN %(from_date)s AND %(to_date)s")
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    if filters.get("purpose"):
        conditions.append("se.purpose = %(purpose)s")
        values["purpose"] = filters.get("purpose")

    condition_string = " AND ".join(conditions)
    if condition_string:
        condition_string = "WHERE " + condition_string

    query = f"""
        SELECT 
            se.name AS stock_entry,
            se.posting_date,
            se.posting_time,
            se.purpose,
            CASE 
                WHEN se.docstatus = 0 THEN 'Draft'
                WHEN se.docstatus = 1 THEN 'Submitted'
                WHEN se.docstatus = 2 THEN 'Cancelled'
            END AS document_status,
            sei.item_code,
            item.item_name,
            sei.qty,
            sei.uom,
            sei.basic_rate AS unit_rate,
            (sei.qty * sei.basic_rate) AS total_cost,
            sei.s_warehouse AS source_warehouse,
            sei.t_warehouse AS target_warehouse,
            sei.cost_center,
            se.project,
            sei.expense_account AS gl_account,
            se.owner AS created_by
        FROM 
            `tabStock Entry` se
        JOIN 
            `tabStock Entry Detail` sei ON se.name = sei.parent
        JOIN 
            `tabItem` item ON sei.item_code = item.item_code
        {condition_string}
        ORDER BY 
            se.posting_date DESC, se.posting_time DESC
    """
    
    return frappe.db.sql(query, values, as_dict=True)
