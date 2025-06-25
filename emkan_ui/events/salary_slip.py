import frappe
from frappe.utils import getdate, add_days


def set_leave_settlement_dates(doc, method):
    if doc.payroll_entry:
        doc.salary_structure = "Default"
        apply_leave_adjustment(doc)
        return

    leave = frappe.get_all(
        "Leave Application",
        filters={
            "employee": doc.employee,
            "status": "Approved",
            "leave_type": "Annual Leave (Encashment)"
        },
        fields=["from_date", "to_date", "total_leave_days"],
        order_by="creation desc",
        limit=1
    )

    if leave:
        from_date = getdate(leave[0].from_date)
        start_date = from_date.replace(day=1)
        end_date = add_days(from_date, -1)

        doc.start_date = start_date
        doc.end_date = end_date
        doc.custom_leave_settlement_paid_days = leave[0].total_leave_days
        doc.salary_structure = "Leave Settlement"


def apply_leave_adjustment(doc):
    leave_slips = frappe.get_all(
        "Salary Slip",
        filters={
            "employee": doc.employee,
            "salary_structure": "Leave Settlement",
            "docstatus": 1
        },
        fields=["name", "total_working_days", "custom_leave_settlement_paid_days"]
    )

    if leave_slips:
        total_deduction = 0
        for slip in leave_slips:
            working_days = slip.total_working_days or 0
            leave_days = slip.custom_leave_settlement_paid_days or 0
            total_deduction += working_days + leave_days

        original_payment_days = doc.payment_days or 0
        adjusted_payment_days = original_payment_days - total_deduction
        if adjusted_payment_days < 0:
            adjusted_payment_days = 0

        doc.payment_days = adjusted_payment_days

        # frappe.msgprint(f"Adjusted payment days by {total_deduction} due to Leave Settlement Salary Slip.")


@frappe.whitelist()
def get_encashment_leave(employee):
    leave = frappe.get_all(
        "Leave Application",
        filters={
            "employee": employee,
            "status": "Approved",
            "leave_type": "Annual Leave (Encashment)"
        },
        fields=["from_date", "to_date", "total_leave_days"],
        order_by="creation desc",
        limit=1
    )

    if leave:
        from_date = getdate(leave[0].from_date)
        start_date = from_date.replace(day=1)
        end_date = add_days(from_date, -1)

        return {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "from_date": str(leave[0].from_date),
            "to_date": str(leave[0].to_date),
            "total_leave_days": leave[0].total_leave_days
        }

    return {}
