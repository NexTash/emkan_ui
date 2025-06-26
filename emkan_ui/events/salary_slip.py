import frappe
from frappe.utils import getdate, add_days, date_diff, nowdate


def set_leave_settlement_dates(doc, method):
    if doc.payroll_entry:
        doc.salary_structure = "Default"
        apply_leave_adjustment(doc)
        apply_dynamic_month_lwp(doc)
        apply_rejoining_lwp(doc)
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


def apply_dynamic_month_lwp(doc):
    leave = frappe.get_all(
        "Leave Application",
        filters={
            "employee": doc.employee,
            "status": "Approved",
            "leave_type": "Annual Leave (Encashment)"
        },
        fields=["to_date"],
        order_by="creation desc",
        limit=1
    )

    if not leave:
        return

    leave_to_date = getdate(leave[0].to_date)
    leave_end_plus_one = add_days(leave_to_date, 1)

    rejoining = frappe.get_all(
        "Employee Rejoining",
        filters={"employee": doc.employee},
        fields=["return_date"],
        order_by="creation desc",
        limit=1
    )

    rejoined = False
    if rejoining and rejoining[0].return_date:
        return_date = getdate(rejoining[0].return_date)
        if return_date <= getdate(doc.end_date):
            rejoined = True

    if not rejoined:
        today = getdate(nowdate())
        salary_end = getdate(doc.end_date)

        calculation_end_date = today if salary_end >= today else salary_end

        if leave_end_plus_one <= calculation_end_date:
            days_to_deduct = date_diff(calculation_end_date, leave_end_plus_one) + 1

            current_lwp = doc.leave_without_pay or 0
            current_payment_days = doc.payment_days or 0

            doc.leave_without_pay = current_lwp + days_to_deduct

            adjusted_payment_days = current_payment_days - days_to_deduct
            if adjusted_payment_days < 0:
                adjusted_payment_days = 0

            doc.payment_days = adjusted_payment_days


def apply_rejoining_lwp(doc):
    leave = frappe.get_all(
        "Leave Application",
        filters={
            "employee": doc.employee,
            "status": "Approved",
            "leave_type": "Annual Leave (Encashment)"
        },
        fields=["from_date", "to_date"],
        order_by="creation desc",
        limit=1
    )

    if not leave:
        return

    rejoining = frappe.get_all(
        "Employee Rejoining",
        filters={"employee": doc.employee},
        fields=["expected_end_date", "return_date"],
        order_by="creation desc",
        limit=1
    )

    if rejoining:
        expected_end = getdate(rejoining[0].expected_end_date) if rejoining[0].expected_end_date else None
        return_date = getdate(rejoining[0].return_date) if rejoining[0].return_date else None

        if expected_end and return_date:
            days_late = date_diff(return_date, expected_end)

            if days_late > 1:
                lwp_days = days_late - 1

                current_lwp = doc.leave_without_pay or 0
                doc.leave_without_pay = current_lwp + lwp_days

                current_payment_days = doc.payment_days or 0
                adjusted_payment_days = current_payment_days - lwp_days
                if adjusted_payment_days < 0:
                    adjusted_payment_days = 0
                doc.payment_days = adjusted_payment_days


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
