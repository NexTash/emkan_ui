
import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        
        {"label": "REVENUE", "fieldname": "revenue", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN-1 - EECS", "fieldname": "emkan_1_income", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN-2 - EECS", "fieldname": "emkan_2_income", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN-3 (SSSF) - EECS", "fieldname": "emkan_3_income", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN-4 (BSI) - EECS", "fieldname": "emkan_4_income", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN -5 - EECS", "fieldname": "emkan_5_income", "fieldtype": "Data", "width": 150},
        
        
        {"label": "Expense", "fieldname": "direct_expense", "fieldtype": "Currency", "width": 150},
        {"label": "Common Projects", "fieldname": "project", "fieldtype": "Data", "width": 150},
        # {"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 150},
        {"label": "Income", "fieldname": "total_income", "fieldtype": "Currency", "width": 150},
        # {"label": "InDirect Expense", "fieldname": "indirect_expense", "fieldtype": "Currency", "width": 150},
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
                WHEN gle.cost_center = 'EMKAN-1 - EECS' THEN gle.project 
                ELSE NULL 
            END AS emkan_1,

            CASE 
                WHEN gle.cost_center = 'EMKAN-2 - EECS' THEN gle.project 
                ELSE NULL 
            END AS emkan_2,

            CASE 
                WHEN gle.cost_center = 'EMKAN-3 (SSSF) - EECS' THEN gle.project 
                ELSE NULL 
            END AS emkan_3,

            CASE 
                WHEN gle.cost_center = 'EMKAN-4 (BSI) - EECS' THEN gle.project 
                ELSE NULL 
            END AS emkan_4,

            CASE 
                WHEN gle.cost_center = 'EMKAN -5 - EECS' THEN gle.project 
                ELSE NULL 
            END AS emkan_5,

            gle.project AS project,

            -- Fixing COALESCE usage
            COALESCE(
                CASE 
                    WHEN gle.cost_center IN ('EMKAN-1 - EECS', 'EMKAN-2 - EECS', 'EMKAN-3 (SSSF) - EECS', 
                                            'EMKAN-4 (BSI) - EECS', 'EMKAN -5 - EECS') 
                    THEN gle.project
                    ELSE NULL
                END, gle.cost_center
            ) AS revenue,

            -- Income, Direct Expense, Indirect Expense, and Total Expense calculations
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
                    WHEN acc.root_type = 'Expense' THEN gle.debit - gle.credit
                    ELSE 0
                END) AS total_expense,

            (SUM(CASE 
                    WHEN acc.root_type = 'Income' THEN gle.credit - gle.debit
                    ELSE 0
                END) - 
            SUM(CASE 
                    WHEN acc.root_type = 'Expense' THEN gle.debit - gle.credit
                    ELSE 0
                END)) AS net_income_loss

        FROM 
            `tabGL Entry` AS gle
        INNER JOIN 
            `tabAccount` AS acc ON gle.account = acc.name
        WHERE 
            acc.report_type = 'Profit and Loss'
            AND gle.cost_center IN (
                'EMKAN-1 - EECS', 
                'EMKAN-2 - EECS', 
                'EMKAN-3 (SSSF) - EECS', 
                'EMKAN-4 (BSI) - EECS', 
                'EMKAN -5 - EECS'
            )
            AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
        GROUP BY 
            gle.cost_center, gle.project;

    """
    # frappe.msgprint(f"{query}")
    result = frappe.db.sql(query, filters, as_dict=True)
    # frappe.msgprint(f"results          :        {result}")

    # Initializing variables to store sums
    emkan_1_income = 0
    emkan_2_income = 0
    emkan_3_income = 0
    emkan_4_income = 0
    emkan_5_income = 0
    emkan_1_direct_expense = 0
    emkan_2_direct_expense = 0
    emkan_3_direct_expense = 0
    emkan_4_direct_expense = 0
    emkan_5_direct_expense = 0
    
    total_income_sum = 0
    indirect_expense_sum = 0
    total_expense_sum = 0

    # Sum the values for each column
    for entry in result:
        if entry['emkan_1'] is not None:
            emkan_1_income += flt(entry['total_income'])
            emkan_1_direct_expense += flt(entry['direct_expense'])
            
        if entry['emkan_2'] is not None:
            emkan_2_income += flt(entry['total_income'])
            emkan_2_direct_expense += flt(entry['direct_expense'])
        if entry['emkan_3'] is not None:
            emkan_3_income += flt(entry['total_income'])
            emkan_3_direct_expense += flt(entry['direct_expense'])
        if entry['emkan_4'] is not None:
            emkan_4_income += flt(entry['total_income'])
            emkan_4_direct_expense += flt(entry['direct_expense'])
        if entry['total_income'] and entry['emkan_5'] is None:
            emkan_5_income += flt(entry['total_income'])
            emkan_5_direct_expense += flt(entry['direct_expense'])

        total_income_sum += flt(entry.get('total_income', 0))
        indirect_expense_sum += flt(entry.get('indirect_expense', 0))
        total_expense_sum += flt(entry.get('total_expense', 0))

    direct_expense = {
        "revenue": "Direct Exp",
        "emkan_1": emkan_1_direct_expense,
        "emkan_2": emkan_2_direct_expense,
        "emkan_3": emkan_3_direct_expense,
        "emkan_4": emkan_4_direct_expense,
        "emkan_5": emkan_5_direct_expense,
        "project": "Total",
        "indirect_expense": indirect_expense_sum,
        "total_expense": total_expense_sum,
        "total" : emkan_1_direct_expense+emkan_2_direct_expense+emkan_3_direct_expense+emkan_4_direct_expense+emkan_5_direct_expense
    }


    # Adding the summed values as a row
    income = {
        "revenue": "REVENUE",
        "emkan_1": "rniweubruib" ,
        "emkan_2": "rniweubruib ",
        "emkan_3": emkan_3_income,
        "emkan_4": emkan_4_income,
        "emkan_5": emkan_5_income,
        "project": "Total",
        "indirect_expense": indirect_expense_sum,
        "total_expense": total_expense_sum,
        "total" : emkan_1_income+emkan_2_income+emkan_3_income+emkan_4_income+emkan_5_income
    }

    frappe.msgprint(f"direct_expense :{result}")
    
    result.append( income)
    result.append(direct_expense) 


    for entry in result:
        total_income = entry.get("total_income", 0)

        for i in range(1, 6):
            key = f"emkan_{i}"
            if entry.get(key):
                entry[f"{key}_income"] = total_income
            else:
                entry[f"{key}_income"] = None


    frappe.msgprint(f"# Explicitly set to None : {result}")


    return result

