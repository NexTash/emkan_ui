import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    raw_data = get_data(filters)
    data = merge_matching_divisions(raw_data)
    return columns, data

def get_columns():
    return [
        {"label": _("Division"), "fieldname": "division", "fieldtype": "Data", "width": 200},
        {"label": _("Project"), "fieldname": "project", "fieldtype": "Data", "width": 200},
        # {"label": _("Parent Account"), "fieldname": "parent_account", "fieldtype": "Link", "options": "Account", "width": 200},
        {"label": _("Revenue (Income)"), "fieldname": "revenue", "fieldtype": "Currency", "width": 150},
        {"label": _("Direct Expense"), "fieldname": "direct_expense", "fieldtype": "Currency", "width": 150},
        {"label": _("Indirect Expense"), "fieldname": "indirect_expense", "fieldtype": "Currency", "width": 150},
        {"label": _("Other Expenses"), "fieldname": "other_expenses", "fieldtype": "Currency", "width": 150},
        {"label": _("Profit & Loss"), "fieldname": "profit_loss", "fieldtype": "Currency", "width": 150},
    ]

def get_data(filters):
    conditions = "1=1"
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND gl.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("cost_center"):
        conditions += " AND gl.cost_center = %(cost_center)s"
    if filters.get("project"):
        conditions += " AND gl.project = %(project)s"

    # Fetch account types dynamically (Revenue, Direct Expense, Indirect Expense, etc.)
    expense_types = get_expense_types()

    query = f"""
        SELECT 
            gl.cost_center AS division,
            gl.project,
            gl.account,
            acc.parent_account,
            SUM(gl.debit) AS revenue,
            SUM(CASE WHEN acc.account_type = '{expense_types['direct_expense']}' THEN gl.credit ELSE 0 END) AS direct_expense,
            SUM(CASE WHEN acc.account_type = '{expense_types['indirect_expense']}' THEN gl.credit ELSE 0 END) AS indirect_expense,
            SUM(CASE WHEN acc.account_type NOT IN ('{expense_types['direct_expense']}', '{expense_types['indirect_expense']}') AND acc.account_type != '{expense_types['revenue']}' THEN gl.credit ELSE 0 END) AS other_expenses,
            SUM(gl.debit - gl.credit) AS balance
        FROM 
            `tabGL Entry` AS gl
        JOIN 
            `tabAccount` AS acc ON acc.name = gl.account
        WHERE {conditions}
        GROUP BY 
            gl.cost_center, gl.project, gl.account, acc.parent_account
    """

    data = frappe.db.sql(query, filters, as_dict=True)
    return data

def get_expense_types():
    """Fetch the account types for Revenue, Direct Expense, Indirect Expense, and Other Expenses dynamically"""
    expense_types = {
        "revenue": "Revenue",  # Replace these with the actual account type names used in your system
        "direct_expense": "Direct Expense",  # Replace these with the actual account types
        "indirect_expense": "Indirect Expense",  # Replace these with the actual account types
        "other_expenses": "Other Expense"  # Replace these with the actual account types
    }

    return expense_types

def merge_matching_divisions(data):
    merged_data = {}
    
    for row in data:
        key = (row["division"])  # Group by division
        if key not in merged_data:
            merged_data[key] = {
                "division": row["division"],
                "project": row["project"],  # Optionally retain one project's value
                "parent_account": row["parent_account"],
                "revenue": row["revenue"] or 0,
                "direct_expense": row["direct_expense"] or 0,
                "indirect_expense": row["indirect_expense"] or 0,
                "other_expenses": row["other_expenses"] or 0,
                "profit_loss": row["revenue"] - (row["direct_expense"] + row["indirect_expense"] + row["other_expenses"]),
            }
        else:
            merged_data[key]["revenue"] += row["revenue"] or 0
            merged_data[key]["direct_expense"] += row["direct_expense"] or 0
            merged_data[key]["indirect_expense"] += row["indirect_expense"] or 0
            merged_data[key]["other_expenses"] += row["other_expenses"] or 0
            merged_data[key]["profit_loss"] = merged_data[key]["revenue"] - (
                merged_data[key]["direct_expense"] + merged_data[key]["indirect_expense"] + merged_data[key]["other_expenses"]
            )

    return list(merged_data.values())