import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Division", "fieldname": "division", "fieldtype": "Data", "width": 200},
        {"label": "Project", "fieldname": "project", "fieldtype": "Data", "width": 200},
        {"label": "Income", "fieldname": "total_income", "fieldtype": "Currency", "width": 200},
        {"label": "Expense", "fieldname": "total_expense", "fieldtype": "Currency", "width": 200},
        {"label": "Profit", "fieldname": "net_income_loss", "fieldtype": "Currency", "width": 200},
    ]

def get_data(filters):
    conditions = "1=1"
    
    # Add conditions based on the filters provided
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("cost_center"):
        conditions += " AND gle.cost_center = %(cost_center)s"
    if filters.get("project"):
        conditions += " AND gle.project = %(project)s"  # This line is now guarded by a check for "project"
    
    # Construct the query
    query = f"""
        SELECT 
            gle.cost_center AS division,
            gle.project AS project,
            SUM(CASE 
                    WHEN acc.root_type = 'Income' THEN gle.credit - gle.debit
                    ELSE 0
                END) AS total_income,
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
            gle.cost_center, gle.project
    """
    
    # Execute the query
    result = frappe.db.sql(query, filters, as_dict=True)

    return result
