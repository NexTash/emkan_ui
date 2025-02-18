import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        
        {"label": "", "fieldname": "static_field", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN-1 - EECS", "fieldname": "emkan_1", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN-2 - EECS", "fieldname": "emkan_2", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN-3 (SSSF) - EECS", "fieldname": "emkan_3", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN-4 (BSI) - EECS", "fieldname": "emkan_4", "fieldtype": "Data", "width": 150},
        {"label": "EMKAN -5 - EECS", "fieldname": "emkan_5", "fieldtype": "Data", "width": 150},
        {"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 150},
        
        
        # {"label": "Total Expense", "fieldname": "total_expense", "fieldtype": "Currency", "width": 200},
        {"label": "Common Projects", "fieldname": "project", "fieldtype": "Data", "width": 200},
        # {"label": "Income", "fieldname": "total_income", "fieldtype": "Currency", "width": 200},
        # {"label": "InDirect Expense", "fieldname": "indirect_expense", "fieldtype": "Currency", "width": 200},
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
            -- Total Income, Direct Expense, Indirect Expense, and Total Expense calculations remain the same
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
        if entry['emkan_5'] is not None:
            emkan_5_income += flt(entry['total_income'])
            emkan_5_direct_expense += flt(entry['direct_expense'])

        total_income_sum += flt(entry.get('total_income', 0))
        indirect_expense_sum += flt(entry.get('indirect_expense', 0))
        total_expense_sum += flt(entry.get('total_expense', 0))
    direct_expense = {
        "static_field": "Direct Exp",
        "emkan_1": emkan_1_direct_expense,
        "emkan_2": emkan_2_direct_expense,
        "emkan_3": emkan_3_direct_expense,
        "emkan_4": emkan_4_direct_expense,
        "emkan_5": emkan_5_direct_expense,
        # "project": "Total",
        # "indirect_expense": indirect_expense_sum,
        # "total_expense": total_expense_sum,
        # "total" : emkan_1_direct_expense+emkan_2_direct_expense+emkan_3_direct_expense+emkan_4_direct_expense+emkan_5_direct_expense
    }

    # Adding the summed values as a row
    income = {
        "static_field": "REVENEU",
        "emkan_1": emkan_1_income,
        "emkan_2": emkan_2_income,
        "emkan_3": emkan_3_income,
        "emkan_4": emkan_4_income,
        "emkan_5": emkan_5_income,
        # "project": "Total",
        # "indirect_expense": indirect_expense_sum,
        # "total_expense": total_expense_sum,
        # "total" : emkan_1_income+emkan_2_income+emkan_3_income+emkan_4_income+emkan_5_income
    }

    # Append the totals row
    # result.insert(0, income)
    # result.append(direct_expense) 
    data = []
    keys = ["emkan_0", "emkan_1", "emkan_2", "emkan_3", "emkan_4", "emkan_5"]
    current_dict = {}

    for doc in result:
        for key in keys:
            if key in doc and doc[key] is not None:
                if key in current_dict:
                    current_dict[key].append(doc[key])
                else:
                    current_dict[key] = [doc[key]]

    max_len = max(len(values) for values in current_dict.values())

    for i in range(max_len):
        new_dict = {}
        for key in keys:
            if key in current_dict and i < len(current_dict[key]):
                new_dict[key] = current_dict[key][i]
            else:
                new_dict[key] = None
        
        value_count = {}
        
        for k, v in new_dict.items():
            if v is not None:
                if v in value_count:
                    value_count[v].append(k)
                else:
                    value_count[v] = [k]

        common_values = []
        
        for val, keys_list in value_count.items():
            if len(keys_list) > 1:
                common_values.append(val)

        if common_values:
            new_dict["project"] = ", ".join(common_values)

        data.append(new_dict)


    # frappe.msgprint(f"Transformed data: {data}")
    data.insert(0, income)
    data.append(direct_expense) 



    return data



