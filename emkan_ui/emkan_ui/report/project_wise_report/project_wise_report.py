#  Copyright (c) 2025, NexTash and contributors
#  For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 350, "align": "left"},
        {"label": "Income", "fieldname": "total_income", "fieldtype": "Currency", "width": 200, "align": "right"},
        {"label": "Direct Expense", "fieldname": "direct_expense", "fieldtype": "Currency", "width": 200, "align": "right"},
        {"label": "InDirect Expense", "fieldname": "indirect_expense", "fieldtype": "Currency", "width": 200, "align": "right"},
        {"label": "Other Expense", "fieldname": "other_expense", "fieldtype": "Currency", "width": 200, "align": "right"},
        {"label": "Total Expense", "fieldname": "total_expense", "fieldtype": "Currency", "width": 200, "align": "right"},
        {"label": "Profit/Loss", "fieldname": "net_income_loss", "fieldtype": "Currency", "width": 200, "align": "right"},
    ]

def get_data(filters):
    conditions = "1=1"
    
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("project"):
        conditions += " AND gle.project = %(project)s"
    if filters.get("account"):
        conditions += " AND gle.account = %(account)s"
    
    query = f"""
        SELECT 
            gle.project AS project,
            SUM(CASE 
                    WHEN acc.root_type = 'Income' THEN gle.credit - gle.debit
                    ELSE 0
                END) AS total_income,
            SUM(CASE 
                    WHEN acc.parent_account = '5001 - DIRECT EXPENSES - EECS' THEN gle.debit - gle.credit
                    ELSE 0
                END) AS direct_expense,
            SUM(CASE 
                    WHEN acc.parent_account = '5002 - INDIRECT EXPENSES - EECS' THEN gle.debit - gle.credit
                    ELSE 0
                END) AS indirect_expense,
            SUM(CASE 
                    WHEN acc.root_type = 'Expense' 
                        AND acc.parent_account NOT IN ('5001 - DIRECT EXPENSES - EECS', '5002 - INDIRECT EXPENSES - EECS')
                    THEN gle.debit - gle.credit
                    ELSE 0
                END) AS other_expense,
            SUM(CASE 
                    WHEN acc.root_type = 'Expense' THEN gle.debit - gle.credit
                    ELSE 0
                END) AS total_expense,
            SUM(CASE 
                    WHEN acc.root_type = 'Income' THEN gle.credit - gle.debit
                    ELSE 0
                END) - 
            SUM(CASE 
                    WHEN acc.root_type = 'Expense' THEN gle.debit - gle.credit
                    ELSE 0
                END) AS net_income_loss
        FROM 
            `tabGL Entry` AS gle
        INNER JOIN 
            `tabAccount` AS acc ON gle.account = acc.name
        WHERE 
            acc.report_type = 'Profit and Loss'
            AND {conditions}
        GROUP BY 
            gle.project
        ORDER BY 
            gle.project
    """
    
    result = frappe.db.sql(query, filters, as_dict=True)
    
    return [
        row for row in result 
        if not (
            flt(row["total_income"]) == 0 and 
            flt(row["total_expense"]) == 0 and 
            flt(row["net_income_loss"]) == 0
        )
    ]
