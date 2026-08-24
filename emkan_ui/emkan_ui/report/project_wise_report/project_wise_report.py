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
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 300, "align": "left"},
        {"label": "Estimated Costing", "fieldname": "estimated_costing", "fieldtype": "Currency", "width": 200, "align": "right"},
        {"label": "Project Value", "fieldname": "total_sales_amount", "fieldtype": "Currency", "width": 200, "align": "right"},
        {"label": "Gross Income", "fieldname": "gross_income", "fieldtype": "Currency", "width": 200, "align": "right"},
        {"label": "Net Income", "fieldname": "net_income", "fieldtype": "Currency", "width": 200, "align": "right"},
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
                END) AS total_expense
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

    # Build Sales Invoice date/project conditions separately (no `gle`/`account` filter here)
    si_conditions = "si.docstatus = 1"
    if filters.get("from_date") and filters.get("to_date"):
        si_conditions += " AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s"

    si_query = f"""
        SELECT 
            si.project AS project,
            SUM(si.base_total) AS gross_income,
            SUM(si.base_grand_total) AS net_income
        FROM 
            `tabSales Invoice` AS si
        WHERE 
            {si_conditions}
            AND si.project IS NOT NULL
            AND si.project != ''
        GROUP BY 
            si.project
    """

    si_result = frappe.db.sql(si_query, filters, as_dict=True)
    si_map = {row["project"]: row for row in si_result}

    for row in result:
        if row.get("project"):
            project = frappe.db.get_value(
                "Project",
                row["project"],
                ["estimated_costing", "total_sales_amount"],
                as_dict=True,
            ) or {}
            row["estimated_costing"] = flt(project.get("estimated_costing"))
            row["total_sales_amount"] = flt(project.get("total_sales_amount"))
        else:
            row["estimated_costing"] = 0
            row["total_sales_amount"] = 0

        si_row = si_map.get(row.get("project"), {})
        row["gross_income"] = flt(si_row.get("gross_income"))
        row["net_income"] = flt(si_row.get("net_income"))
        row["net_income_loss"] = flt(row["net_income"]) - flt(row["total_expense"])

    # Include any project that has Sales Invoice income but no GL Entry rows at all
    existing_projects = {row["project"] for row in result}
    for project, si_row in si_map.items():
        if project not in existing_projects:
            proj = frappe.db.get_value(
                "Project",
                project,
                ["estimated_costing", "total_sales_amount"],
                as_dict=True,
            ) or {}
            result.append({
                "project": project,
                "estimated_costing": flt(proj.get("estimated_costing")),
                "total_sales_amount": flt(proj.get("total_sales_amount")),
                "gross_income": flt(si_row.get("gross_income")),
                "net_income": flt(si_row.get("net_income")),
                "direct_expense": 0,
                "indirect_expense": 0,
                "other_expense": 0,
                "total_expense": 0,
                "net_income_loss": flt(si_row.get("net_income")),
            })

    return [
        row for row in result 
        if not (
            flt(row["gross_income"]) == 0 and 
            flt(row["net_income"]) == 0 and 
            flt(row["total_expense"]) == 0 and 
            flt(row["net_income_loss"]) == 0
        )
    ]