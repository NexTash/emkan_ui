import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
		{"label": "", "fieldname": "static_field", "fieldtype": "Data", "width": 160},
        {"label": "EMKAN-1 - EECS", "fieldname": "emkan_1", "fieldtype": "Data", "width": 160},
        {"label": "EMKAN-2 - EECS", "fieldname": "emkan_2", "fieldtype": "Data", "width": 160},
        {"label": "EMKAN-3 (SSSF) - EECS", "fieldname": "emkan_3", "fieldtype": "Data", "width": 160},
        {"label": "EMKAN-4 (BSI) - EECS", "fieldname": "emkan_4", "fieldtype": "Data", "width": 160},
        {"label": "EMKAN -5 - EECS", "fieldname": "emkan_5", "fieldtype": "Data", "width": 160},
        {"label": "Common Projects", "fieldname": "project", "fieldtype": "Data", "width": 200},
		{"label": "Income", "fieldname": "total_income", "fieldtype": "Currency", "width": 200},
        {"label": "InDirect Expense", "fieldname": "indirect_expense", "fieldtype": "Currency", "width": 200},
        {"label": "Total Expense", "fieldname": "total_expense", "fieldtype": "Currency", "width": 200},
    ]

def get_data(filters):
    conditions = """
        gle.cost_center IN (
            'EMKAN-1 - EECS', 
            'EMKAN-2 - EECS', 
            'EMKAN-3 (SSSF) - EECS', 
            'EMKAN-4 (BSI) - EECS', 
            'EMKAN -5 - EECS'
        )
    """

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s"
    if filters.get("cost_center"):
        conditions += " AND gle.cost_center = %(cost_center)s"
    if filters.get("division"):
        conditions += " AND gle.cost_center = %(division)s"
    if filters.get("account"):
        conditions += " AND gle.account = %(account)s"
    
    query = f"""
        SELECT 
            CASE 
                WHEN gle.cost_center = 'EMKAN-1 - EECS' THEN gle.cost_center 
                ELSE NULL 
            END AS emkan_1,
            CASE 
                WHEN gle.cost_center = 'EMKAN-2 - EECS' THEN gle.cost_center 
                ELSE NULL 
            END AS emkan_2,
            CASE 
                WHEN gle.cost_center = 'EMKAN-3 (SSSF) - EECS' THEN gle.cost_center 
                ELSE NULL 
            END AS emkan_3,
            CASE 
                WHEN gle.cost_center = 'EMKAN-4 (BSI) - EECS' THEN gle.cost_center 
                ELSE NULL 
            END AS emkan_4,
            CASE 
                WHEN gle.cost_center = 'EMKAN -5 - EECS' THEN gle.cost_center 
                ELSE NULL 
            END AS emkan_5,
            gle.project AS project,
            
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
            gle.cost_center, gle.project
    """
    
    result = frappe.db.sql(query, filters, as_dict=True)

    # Static row to be prepended
    static_row = {
		"static_field": "REVENUE",
        "emkan_1": "n534" or None,
        "emkan_2": "n534" or None,
        "emkan_3": "n534" or None,
        "emkan_4": "n534" or None,
        "emkan_5": "n534" or None,
        "project": "Static Data",
        "indirect_expense": 0,
        "total_expense": 0
    }

    # Prepend the static row to the result
    result.insert(0, static_row)

    return result
