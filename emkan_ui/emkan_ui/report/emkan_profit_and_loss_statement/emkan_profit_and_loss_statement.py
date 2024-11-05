# Copyright (c) 2024, NexTash and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import (
    get_columns,
    get_data,
    get_period_list,
)

def execute(filters=None):
    period_list = get_period_list(
        filters.from_fiscal_year,
        filters.to_fiscal_year,
        filters.period_start_date,
        filters.period_end_date,
        filters.filter_based_on,
        filters.periodicity,
        company=filters.company,
    )

    # Get Income and Expense data
    income = get_data(
        filters.company,
        "Income",
        "Credit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )

    expense = get_data(
        filters.company,
        "Expense",
        "Debit",
        period_list,
        filters=filters,
        accumulated_values=filters.accumulated_values,
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    )

    # Separate direct and indirect expenses
    direct_expenses = [exp for exp in expense if "Direct Expense" in exp.get("account_type", "")]
    indirect_expenses = [exp for exp in expense if "Indirect Expense" in exp.get("account_type", "")]

    # Summing up the required values
    total_sales = flt(sum(item.get("credit", 0) for item in income))
    total_direct_expense = flt(sum(item.get("debit", 0) for item in direct_expenses))
    gross_profit = flt(total_sales - total_direct_expense)
    total_indirect_expense = flt(sum(item.get("debit", 0) for item in indirect_expenses))
    total_expense = flt(total_direct_expense + total_indirect_expense)
    net_profit = flt(total_sales - total_expense)

    # Organize data with headers
    data = [
        {"account_name": _("1. Sales Revenue"), "is_group": True, "indent": 0},
        *income,
        {"account_name": _("A. Total Sales"), "credit": total_sales, "indent": 1},
        
        {"account_name": _("2. Expenses"), "is_group": True, "indent": 0},
        {"account_name": _("2.1 Direct Expense"), "is_group": True, "indent": 1},
        *direct_expenses,
        {"account_name": _("B. Total Direct Expense"), "debit": total_direct_expense, "indent": 2},
        
        {"account_name": _("C. Gross Profit (A - B)"), "debit": gross_profit, "indent": 1},
        
        {"account_name": _("2.2 Indirect Expense"), "is_group": True, "indent": 1},
        *indirect_expenses,
        {"account_name": _("D. Total Indirect Expense"), "debit": total_indirect_expense, "indent": 2},
        
        {"account_name": _("E. Total Expense (B + D)"), "debit": total_expense, "indent": 1},
        {"account_name": _("Net Profit (A - E)"), "debit": net_profit, "indent": 0, "indicator": "Green" if net_profit > 0 else "Red"},
    ]

    # Get columns for the report
    columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)
    
    return columns, data, None


def get_report_summary(
    period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False
):
    net_income, net_expense, net_profit = 0.0, 0.0, 0.0

    if filters.accumulated_values:
        key = period_list[-1].key
        if income:
            net_income = flt(income[-1].get(key, 0))
        if expense:
            net_expense = flt(expense[-1].get(key, 0))
        if net_profit_loss:
            net_profit = flt(net_profit_loss.get(key, 0))
    else:
        for period in period_list:
            key = period.key
            net_income += flt(income[-1].get(key, 0) if income else 0)
            net_expense += flt(expense[-1].get(key, 0) if expense else 0)
            net_profit += flt(net_profit_loss.get(key, 0) if net_profit_loss else 0)

    profit_label = _("Net Profit") if len(period_list) > 1 else _("Profit This Year")
    income_label = _("Total Income") if len(period_list) > 1 else _("Total Income This Year")
    expense_label = _("Total Expense") if len(period_list) > 1 else _("Total Expense This Year")

    return [
        {"value": net_income, "label": income_label, "datatype": "Currency", "currency": currency},
        {"type": "separator", "value": "-"},
        {"value": net_expense, "label": expense_label, "datatype": "Currency", "currency": currency},
        {"type": "separator", "value": "=", "color": "blue"},
        {
            "value": net_profit,
            "indicator": "Green" if net_profit > 0 else "Red",
            "label": profit_label,
            "datatype": "Currency",
            "currency": currency,
        },
    ], net_profit


def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
    total = 0
    net_profit_loss = {
        "account_name": "'" + _("Profit for the year") + "'",
        "account": "'" + _("Profit for the year") + "'",
        "warn_if_negative": True,
        "currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
    }

    has_value = False

    for period in period_list:
        key = period.key
        total_income = flt(income[-1].get(key, 0)) if income else 0
        total_expense = flt(expense[-1].get(key, 0)) if expense else 0

        net_profit_loss[key] = total_income - total_expense

        if net_profit_loss[key]:
            has_value = True

        total += net_profit_loss[key]
        net_profit_loss["total"] = total

    return net_profit_loss if has_value else None


def get_chart_data(filters, columns, income, direct_expenses, indirect_expenses):
    labels = [d.get("label") for d in columns[2:]]

    income_data = [flt(income[-1].get(p.get("fieldname"), 0)) for p in columns[2:]] if income else []
    direct_expense_data = [flt(direct_expenses[-1].get(p.get("fieldname"), 0)) for p in columns[2:]] if direct_expenses else []
    indirect_expense_data = [flt(indirect_expenses[-1].get(p.get("fieldname"), 0)) for p in columns[2:]] if indirect_expenses else []

    datasets = [
        {"name": _("Income"), "values": income_data},
        {"name": _("Direct Expenses"), "values": direct_expense_data},
        {"name": _("Indirect Expenses"), "values": indirect_expense_data},
    ]

    chart = {
        "data": {"labels": labels, "datasets": datasets},
        "type": "bar" if not filters.accumulated_values else "line",
        "fieldtype": "Currency",
        "options": "currency",
        "currency": filters.presentation_currency or frappe.get_cached_value("Company", filters.company, "default_currency"),
    }

    return chart
