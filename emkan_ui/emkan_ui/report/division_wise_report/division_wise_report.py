import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Division", "fieldname": "division", "fieldtype": "Data", "width": 350},
        {"label": "Income", "fieldname": "total_income", "fieldtype": "Currency", "width": 200},
        {"label": "Direct Expense", "fieldname": "direct_expense", "fieldtype": "Currency", "width": 200},
        {"label": "InDirect Expense", "fieldname": "indirect_expense", "fieldtype": "Currency", "width": 200},
        {"label": "Other Expense", "fieldname": "other_expense", "fieldtype": "Currency", "width": 200},
        {"label": "Total Expense", "fieldname": "total_expense", "fieldtype": "Currency", "width": 200},
        {"label": "Profit/Loss", "fieldname": "net_income_loss", "fieldtype": "Currency", "width": 200},
    ]

def get_data(filters):
    # Base condition
    conditions = "1=1"
    
    # Add conditions for filters
    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("cost_center"):
        conditions += " AND gle.cost_center = %(cost_center)s"
    if filters.get("division"):
        conditions += " AND gle.cost_center = %(division)s"
    if filters.get("account"):
        conditions += " AND gle.account = %(account)s"
    
    # SQL Query with conditions
    query = f"""
        SELECT 
            gle.cost_center AS division,
            
            -- Total Income
            SUM(CASE 
                    WHEN acc.root_type = 'Income' THEN gle.credit - gle.debit
                    ELSE 0
                END) AS total_income,
            
            -- Direct Expense
            SUM(CASE 
                    WHEN acc.parent_account = '5001 - DIRECT EXPENSES - EECS' THEN gle.debit - gle.credit
                    ELSE 0
                END) AS direct_expense,
            
            -- Indirect Expense
            SUM(CASE 
                    WHEN acc.parent_account = '5002 - INDIRECT EXPENSES - EECS' THEN gle.debit - gle.credit
                    ELSE 0
                END) AS indirect_expense,
            
            -- Other Expense
            SUM(CASE 
                    WHEN acc.root_type = 'Expense' 
                        AND acc.parent_account NOT IN ('5001 - DIRECT EXPENSES - EECS', '5002 - INDIRECT EXPENSES - EECS')
                    THEN gle.debit - gle.credit
                    ELSE 0
                END) AS other_expense,
            
            -- Total Expense
            SUM(CASE 
                    WHEN acc.root_type = 'Expense' THEN gle.debit - gle.credit
                    ELSE 0
                END) AS total_expense,
            
            -- Net Income/Loss
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
            gle.cost_center
        ORDER BY 
            gle.cost_center
    """
    
    # Execute the query
    result = frappe.db.sql(query, filters, as_dict=True)
    
    # Filter out rows where all values are zero
    filtered_result = [
        row for row in result 
        if not (
            flt(row["total_income"]) == 0 and 
            flt(row["total_expense"]) == 0 and 
            flt(row["net_income_loss"]) == 0
        )
    ]
    
    return filtered_result
