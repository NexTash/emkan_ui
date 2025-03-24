import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "PROJECTS", "fieldname": "project", "fieldtype": "Data", "width": 170},
        {"label": "EMKAN-1 - EECS", "fieldname": "emkan_1_income", "fieldtype": "Data", "width": 145,},
        {"label": "EMKAN-2 - EECS", "fieldname": "emkan_2_income", "fieldtype": "Data", "width": 145,},
        {"label": "EMKAN-3 (SSSF) - EECS", "fieldname": "emkan_3_income", "fieldtype": "Data", "width": 145,},
        {"label": "EMKAN-4 (BSI) - EECS", "fieldname": "emkan_4_income", "fieldtype": "Data","width": 145,},
        {"label": "EMKAN -5 - EECS", "fieldname": "emkan_5_income", "fieldtype": "Data","width": 145,},
        {"label": "Total", "fieldname": "total", "fieldtype": "Currency", "width": 140},
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
    result = frappe.db.sql(query, filters, as_dict=True)
    
    emkan_divisions = [
    "EMKAN-1 - EECS", "EMKAN-2 - EECS", "EMKAN-3 (SSSF) - EECS",
    "EMKAN-4 (BSI) - EECS", "EMKAN -5 - EECS"
    ]

    data, division_totals, division_direct_exp, division_indirect_exp, project_expenses = [], {}, {}, {}, {}

    for entry in result:
        division = entry.get("division", "")
        total_income = entry.get("total_income", 0)
        direct_expense = entry.get("direct_expense", 0)
        indirect_expense = entry.get("indirect_expense", 0)
        project = entry.get("project", "No Project Selected")

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
            division_direct_exp[division] = division_direct_exp.get(division, 0) + direct_expense
            division_indirect_exp[division] = division_indirect_exp.get(division, 0) + indirect_expense
            
            # Store indirect expenses for each project
            if project not in project_expenses:
                project_expenses[project] = {"direct": {}, "indirect": {}}
            project_expenses[project]["direct"][division] = project_expenses[project]["direct"].get(division, 0) + direct_expense
            project_expenses[project]["indirect"][division] = project_expenses[project]["indirect"].get(division, 0) + indirect_expense

    static_revenue = {"project": "<b>REVENUE</b>", "total": 0}
    static_direct_expense = {"project": "<b>DIRECT EXPENSE</b>", "total": 0}
    static_indirect_expense = {"project": "<b>INDIRECT EXPENSE</b>", "total": 0}
    static_income = {"project": "<b>Total Income</b>", "total": 0}
    static_exp = {"project": "<b>Total Direct Exp</b>", "total": 0}
    static_indirect = {"project": "<b>Total Indirect Expense</b>", "total": 0}
    static_gp = {"project": "<b>GP</b>", "total": 0}
    net_total = {"project": "<b>Net Total</b>", "total": 0}

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

    final_data = [static_revenue]
    project_to_entry_map = {}

    for entry in data:
        project_name = entry.get("project", "No Project Selected")  # Ensuring default value
        division = entry["division"]
        
        if project_name in project_to_entry_map:
            existing_entry = project_to_entry_map[project_name]
            for key in [f"emkan_{i}_income" for i in range(1, 6)]:
                if existing_entry[key] is None and entry[key] is not None:
                    existing_entry[key] = entry[key]
        else:
            new_entry = entry.copy()
            final_data.append(new_entry)
            project_to_entry_map[project_name] = new_entry

    final_data.append(static_income)

    final_data.append({"project": "", "total": ""})
    final_data.append({"project": "<b>Direct Expenses</b>", "total": ""})
    final_data.append({"project": "", "total": ""})

    # Insert project-wise Direct Expenses after Total Income
    for project, expenses in project_expenses.items():
        project_name = project if project else "No Project Selected"
        project_entry = {"project": project_name, "total": ""}
        
        for division, amount in expenses["direct"].items():
            index = emkan_divisions.index(division) + 1 if division in emkan_divisions else None
            if index:
                project_entry[f"emkan_{index}_income"] = amount
        
        final_data.append(project_entry)

    # Insert Total Direct Expenses after project-wise expenses
    final_data.append(static_exp)
    final_data.append(static_gp)
    final_data.append({"project": "", "total": ""})
    final_data.append({"project": "<b>InDirect Expense</b>", "total": ""})
    final_data.append({"project": "", "total": ""})

    # Insert project-wise Indirect Expenses after GP
    for project, expenses in project_expenses.items():
        project_name = project if project else "No Project Selected"
        project_entry = {"project": project_name, "total": ""}
        
        for division, amount in expenses["indirect"].items():
            index = emkan_divisions.index(division) + 1 if division in emkan_divisions else None
            if index:
                project_entry[f"emkan_{index}_income"] = amount
        
        final_data.append(project_entry)

    # Insert Total Indirect Expenses
    final_data.append(static_indirect)
    # final_data.append({"project": "", "total": ""})
    
    final_data.append(net_total)

    return final_data
