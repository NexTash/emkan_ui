import frappe
from frappe.utils import today, getdate, flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "label": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Data",
            "options": "Supplier",
            "width": 200
        },
        {
            "label": "(< 30 Days)",
            "fieldname": "age_0_30",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "30 to 60 Days",
            "fieldname": "age_30_60",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "60 to 90 Days",
            "fieldname": "age_60_90",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "90 to 180 Days",
            "fieldname": "age_90_180",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "(> 180 Days)",
            "fieldname": "age_over_180",
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "label": "Outstanding Amount",
            "fieldname": "outstanding_amount",
            "fieldtype": "Currency",
            "width": 150
        },
    ]

def get_data(filters):
    data = []
    today_date = getdate(today())
    
    conditions = [["status", "=", "Unpaid"]]
    
    if filters.get("supplier"):
        conditions.append(["supplier", "=", filters["supplier"]])

    invoices = frappe.get_all(
        "Purchase Invoice",
        filters=conditions,
        fields=["supplier_name", "name", "posting_date", "due_date", "outstanding_amount"]
    )

    for invoice in invoices:
        outstanding_amount = flt(invoice.outstanding_amount)
        due_date = getdate(invoice.due_date) if invoice.due_date else None
        age_0_30 = age_30_60 = age_60_90 = age_90_180 = age_over_180 = 0

        if due_date:
            age = (today_date - due_date).days

            if 0 <= age <= 30:
                age_0_30 = outstanding_amount
            elif 30 <= age <= 60:
                age_30_60 = outstanding_amount
            elif 60 <= age <= 90:
                age_60_90 = outstanding_amount
            elif 90 <= age <= 180:
                age_90_180 = outstanding_amount
            else:
                age_over_180 = outstanding_amount

        row = {
            "supplier": invoice.supplier_name,
            "invoice_number": invoice.name,
            "outstanding_amount": outstanding_amount,
            "age_0_30": age_0_30,
            "age_30_60": age_30_60,
            "age_60_90": age_60_90,
            "age_90_180": age_90_180,
            "age_over_180": age_over_180
        }
        data.append(row)
    return data