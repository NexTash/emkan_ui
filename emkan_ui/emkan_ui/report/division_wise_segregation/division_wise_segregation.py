import frappe
from frappe.utils import flt


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {"label": "REVENUE", "fieldname": "project", "fieldtype": "Data", "width": 170},
        {
            "label": "EMKAN-1 - EECS",
            "fieldname": "emkan_1_income",
            "fieldtype": "Data",
            "width": 145,
        },
        {
            "label": "EMKAN-2 - EECS",
            "fieldname": "emkan_2_income",
            "fieldtype": "Data",
            "width": 145,
        },
        {
            "label": "EMKAN-3 (SSSF) - EECS",
            "fieldname": "emkan_3_income",
            "fieldtype": "Data",
            "width": 145,
        },
        {
            "label": "EMKAN-4 (BSI) - EECS",
            "fieldname": "emkan_4_income",
            "fieldtype": "Data",
            "width": 145,
        },
        {
            "label": "EMKAN -5 - EECS",
            "fieldname": "emkan_5_income",
            "fieldtype": "Data",
            "width": 145,
        },
        {
            "label": "InDirect Expense",
            "fieldname": "indirect_expense",
            "fieldtype": "Currency",
            "width": 150,
        },
        {"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 140},
        # {"label": "Direct Expense", "fieldname": "direct_expense", "fieldtype": "Currency", "width": 150},
        # {"label": "Division", "fieldname": "division", "fieldtype": "Data", "width":150},
        # {"label": "Project", "fieldname": "project", "fieldtype": "Data", "width": 300},
        # {"label": "Income", "fieldname": "total_income", "fieldtype": "Currency", "width": 150},
        # {"label": "Other Expense", "fieldname": "other_expense", "fieldtype": "Currency", "width": 150},
        # {"label": "Profit/Loss", "fieldname": "net_income_loss", "fieldtype": "Currency", "width": 150},
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
            gle.cost_center, gle.project
    """

    # Execute the query
    result = frappe.db.sql(query, filters, as_dict=True)

    emkan_divisions = [
        "EMKAN-1 - EECS", "EMKAN-2 - EECS", "EMKAN-3 (SSSF) - EECS",
        "EMKAN-4 (BSI) - EECS", "EMKAN -5 - EECS"
    ]
    
    data, division_totals, division_direct_exp, division_indirect_exp = [], {}, {}, {}

    for entry in result:
        division = entry.get("division", "")
        total_income = entry.get("total_income", 0)
        direct_expense = entry.get("direct_expense", 0)
        indirect_expense = entry.get("indirect_expense", 0)  

        if division in emkan_divisions:
            index = emkan_divisions.index(division) + 1
            key = f"emkan_{index}"

            modified_entry = entry.copy()
            for i in range(1, 6):
                modified_entry[f"emkan_{i}"] = None
                modified_entry[f"emkan_{i}_income"] = None

            modified_entry[key] = division
            modified_entry[f"{key}_income"] = total_income

            data.append(modified_entry)
            division_totals[division] = division_totals.get(division, 0) + total_income
            division_direct_exp[division] = (division_direct_exp.get(division, 0) + direct_expense)
            division_indirect_exp[division] = (division_indirect_exp.get(division, 0) + indirect_expense)

    static_income = {"project": "Total Income", "total": 0}
    static_exp = {"project": "Total Direct Exp", "total": 0}
    static_indirect = {"project": "Indirect Expense", "total": 0}
    static_gp = {"project": "GP", "total": 0}
    net_total = {"project": "Net Total", "total": 0}

    for division, total_income in division_totals.items():
        if division in emkan_divisions:
            index = emkan_divisions.index(division) + 1
            static_income[f"emkan_{index}_income"] = total_income

    for division, total_expense in division_direct_exp.items():
        if division in emkan_divisions:
            index = emkan_divisions.index(division) + 1
            static_exp[f"emkan_{index}_income"] = total_expense  

    for division, total_expense in division_indirect_exp.items():
        if division in emkan_divisions:
            index = emkan_divisions.index(division) + 1
            static_indirect[f"emkan_{index}_income"] = total_expense

    total_income = total_expense = total_indirect = 0

    for i in range(1, 6):
        income = static_income.get(f"emkan_{i}_income", 0)
        expense = static_exp.get(f"emkan_{i}_income", 0)
        indirect_expense = static_indirect.get(f"emkan_{i}_income", 0)

        static_gp[f"emkan_{i}_income"] = income - expense
        net_total[f"emkan_{i}_income"] = income - expense - indirect_expense

        total_income += income
        total_expense += expense
        total_indirect += indirect_expense

    static_income["total"] = total_income
    static_exp["total"] = total_expense
    static_indirect["total"] = total_indirect
    static_gp["total"] = total_income - total_expense
    net_total["total"] = total_income - total_expense - total_indirect

    data.append(static_exp)
    data.insert(0, static_income)
    data.append(static_gp)
    data.append(static_indirect)
    data.append(net_total)

    # frappe.msgprint(f"net_total : {net_total}")
    return data
