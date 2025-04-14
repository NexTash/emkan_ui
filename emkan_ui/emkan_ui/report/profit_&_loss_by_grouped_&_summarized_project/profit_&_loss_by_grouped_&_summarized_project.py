# Copyright (c) 2025, NexTash and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Project / Account", "fieldname": "label", "fieldtype": "Data", "width": 300},
        {"label": "Amount", "fieldname": "amount", "fieldtype": "Currency", "width": 200},
        {"label": "Type", "fieldname": "type", "fieldtype": "Data", "width": 200},
        {"label": "Account", "fieldname": "account", "fieldtype": "Data", "hidden": 1}  # Needed for JS routing
    ]

def get_data(filters):
    data = []

    main_categories = [
        {"name": "Income", "root_type": "Income"},
        {"name": "Direct Expense", "parent_account": "5001 - DIRECT EXPENSES - EECS"},
        {"name": "Indirect Expense", "parent_account": "5002 - INDIRECT EXPENSES - EECS"},
        {"name": "Other Expense", "parent_account": None, "exclude_accounts": ['5001 - DIRECT EXPENSES - EECS', '5002 - INDIRECT EXPENSES - EECS']},
    ]

    for cat in main_categories:
        category_total = 0.0

        category_row = {
            "label": cat["name"],
            "amount": 0.0,
            "type": "Grouped & Summarized Project",
            "indent": 0
        }
        data.append(category_row)
        category_index = len(data) - 1

        # Project-level data
        project_query = f"""
            SELECT
                gle.project,
                SUM(gle.debit - gle.credit) AS amount
            FROM `tabGL Entry` gle
            INNER JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE
                acc.root_type = %(root_type)s
                AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
                {"AND acc.parent_account = %(parent_account)s" if cat.get("parent_account") else ""}
                {"AND acc.parent_account NOT IN %(exclude_accounts)s" if cat.get("exclude_accounts") else ""}
                AND gle.project IS NOT NULL
            GROUP BY gle.project
        """

        project_params = {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date"),
            "root_type": cat.get("root_type", "Expense")
        }
        if cat.get("parent_account"):
            project_params["parent_account"] = cat["parent_account"]
        if cat.get("exclude_accounts"):
            project_params["exclude_accounts"] = tuple(cat["exclude_accounts"])

        projects = frappe.db.sql(project_query, project_params, as_dict=True)

        for proj in projects:
            if not proj.project or flt(proj.amount) == 0:
                continue

            project_total = 0.0
            project_row = {
                "label": proj.project,
                "amount": 0.0,
                "type": "",
                "indent": 1
            }
            data.append(project_row)
            project_index = len(data) - 1

            # Account-level data per project
            account_query = f"""
                SELECT
                    gle.account,
                    SUM(gle.debit - gle.credit) AS amount
                FROM `tabGL Entry` gle
                INNER JOIN `tabAccount` acc ON gle.account = acc.name
                WHERE
                    acc.root_type = %(root_type)s
                    {"AND acc.parent_account = %(parent_account)s" if cat.get("parent_account") else ""}
                    {"AND acc.parent_account NOT IN %(exclude_accounts)s" if cat.get("exclude_accounts") else ""}
                    AND gle.project = %(project)s
                    AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
                GROUP BY gle.account
            """

            account_params = {
                "from_date": filters.get("from_date"),
                "to_date": filters.get("to_date"),
                "project": proj.project,
                "root_type": cat.get("root_type", "Expense")
            }
            if cat.get("parent_account"):
                account_params["parent_account"] = cat["parent_account"]
            if cat.get("exclude_accounts"):
                account_params["exclude_accounts"] = tuple(cat["exclude_accounts"])

            accounts = frappe.db.sql(account_query, account_params, as_dict=True)

            for acc in accounts:
                if flt(acc.amount) == 0:
                    continue

                data.append({
                    "label": acc.account,
                    "account": acc.account,
                    "amount": acc.amount,
                    "type": "Grouped & Summarized by Account",
                    "indent": 2
                })
                project_total += acc.amount

            data[project_index]["amount"] = project_total
            category_total += project_total

        data[category_index]["amount"] = category_total

    return data
