# Copyright (c) 2025, NexTash and contributors
# For license information, please see license.txt


import frappe
from frappe.utils import flt, date_diff, getdate

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data

def get_columns():
    return [
        {"label": "Emp ID", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 120},
        {"label": "Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": "Department", "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 150},
        {"label": "Accrual Basis (Basic + HRA)", "fieldname": "accrual_basis", "fieldtype": "Currency", "width": 180},
        {"label": "Accrued Days Per Month", "fieldname": "accrued_days", "fieldtype": "Float", "width": 180},
        {"label": "Accrued Amount Per Month", "fieldname": "accrued_amount", "fieldtype": "Currency", "width": 180},
        {"label": "Total Accrued Days", "fieldname": "total_accrued_days", "fieldtype": "Float", "width": 180},
        {"label": "Total Accrued Amount", "fieldname": "total_accrued_amount", "fieldtype": "Currency", "width": 180}
    ]

def get_data(filters):
    conditions = "1=1"
    if filters.get("company"):
        conditions += f" AND e.company = '{filters.get('company')}'"
    if filters.get("department"):
        conditions += f" AND e.department = '{filters.get('department')}'"
    if filters.get("employee"):
        conditions += f" AND e.name = '{filters.get('employee')}'"
    if filters.get("employee_status") and filters.get("employee_status") != "":
        conditions += f" AND e.status = '{filters.get('employee_status')}'"

    employees = frappe.db.sql(f"""
        SELECT e.name, e.employee_name, e.department, 
            (SELECT ssa.base FROM `tabSalary Structure Assignment` ssa WHERE ssa.employee = e.name ORDER BY ssa.creation DESC LIMIT 1) AS base,
            (SELECT ssa.custom_hra FROM `tabSalary Structure Assignment` ssa WHERE ssa.employee = e.name ORDER BY ssa.creation DESC LIMIT 1) AS custom_hra
        FROM `tabEmployee` e
        WHERE {conditions}
    """, as_dict=True)

    data = []
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    months_elapsed = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month) + 1

    for emp in employees:
        accrual_basis = flt(emp.base) + flt(emp.custom_hra)
        leave_alloc = frappe.get_value("Leave Allocation", {"employee": emp.name, "leave_type": "Annual Leave"}, "total_leaves_allocated") or 0
        accrued_days_per_month = flt(leave_alloc) / 12 if leave_alloc else 0
        amount_per_day = flt(accrual_basis) / 30 if accrual_basis else 0
        accrued_amount_per_month = accrued_days_per_month * amount_per_day

        total_accrued_days = accrued_days_per_month * months_elapsed
        total_accrued_amount = total_accrued_days * amount_per_day

        data.append({
            "employee": emp.name,
            "employee_name": emp.employee_name,
            "department": emp.department,
            "accrual_basis": accrual_basis,
            "accrued_days": accrued_days_per_month,
            "accrued_amount": accrued_amount_per_month,
            "total_accrued_days": total_accrued_days,
            "total_accrued_amount": total_accrued_amount
        })
    
    return data
