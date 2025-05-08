import frappe
from frappe.utils import getdate, date_diff, flt
from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on, LeaveApplication

import frappe
from datetime import datetime

# Custom validation function
def custom_validate(doc, method):
    end_date = getdate(doc.from_date)
    forecasted_balance = get_forecasted_leave_balance(doc, doc.employee, doc.employee_name, end_date)
    total_leave_days = doc.total_leave_days or date_diff(doc.to_date, doc.from_date) + 1
    if total_leave_days > forecasted_balance:
        frappe.throw(f"Cannot apply for {total_leave_days} days. Forecasted balance by {doc.to_date} is only {forecasted_balance:.2f} days.")

# Forecasted leave balance logic
def get_forecasted_leave_balance(doc, employee, employee_name, future_date):
    today = getdate()

    allocations = frappe.db.get_all(
        "Leave Allocation",
        filters={"employee_name": employee_name},
        fields=["total_leaves_allocated", "new_leaves_allocated"],
        order_by="to_date desc",
        limit=1
    )

    allocation = allocations[0] if allocations else {}
    accrual_per_month = flt(allocation.get("total_leaves_allocated", 0))
    leave_balance = flt(2.5)


    if accrual_per_month:
        months_remaining = (future_date.year - today.year) * 12 + future_date.month - today.month
        forecasted_accrual = accrual_per_month + (months_remaining * leave_balance)
        doc.leave_balance = forecasted_accrual
    else:
        forecasted_accrual = leave_balance

    return forecasted_accrual

# ✅ Monkey Patch: Replace the error-throwing function
def custom_show_insufficient_balance_message(self, leave_balance_for_consumption: float) -> None:
    if frappe.db.get_value("Leave Type", self.leave_type, "allow_negative"):
        msg = ("Warning: Insufficient leave balance for Leave Type {0}. You can still apply for leaves.").format(
            frappe.bold(self.leave_type)
        )
    else:
        msg = ("Insufficient leave balance for Leave Type {0}.").format(
            frappe.bold(self.leave_type)
        )

    # 👇 msgprint instead of throw
    frappe.msgprint(msg, title=("Leave Balance Warning"), indicator="orange")

# Patch the original method
LeaveApplication.show_insufficient_balance_message = custom_show_insufficient_balance_message


def store_data(doc, method=None):
    # Get the current timestamp
    timestamp = frappe.utils.now()
    current_date = datetime.now().date()
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)
    if old_doc and doc.workflow_state != old_doc.workflow_state:
        doc.custom_current_workflow_state = doc.workflow_state

        state_exists = False
        for row in doc.custom_workflow_status:
            if row.workflow_states == doc.workflow_state:
                row.approved_by = frappe.session.user
                row.approved_by_name = user_doc.full_name
                row.date = current_date
                state_exists = True
                break
        
        if not state_exists:       
            doc.append("custom_workflow_status", {
                "workflow_states": old_doc.workflow_state,
                "approved_by": frappe.session.user,
                "approved_by_name" : user_doc.full_name,
                "date" : current_date
            })
        else:
            doc.append("custom_workflow_status", {
                "workflow_states": doc.workflow_state,
                "approved_by": frappe.session.user,
                "approved_by_name" : user_doc.full_name,
                "date" : current_date
            })

def last_state(doc, method=None):
    # Get the previous document state
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)
    current_date = datetime.now().date()

    # Proceed if there is a change in workflow_state
    if old_doc and doc.workflow_state != old_doc.workflow_state:
        # Set the custom current workflow state
        doc.custom_current_workflow_state = doc.workflow_state

        # Append COO Approved status to the child table
        if doc.custom_current_workflow_state == "Approved":
            # frappe.throw(f"{doc.custom_current_workflow_state}")
            doc.append("custom_workflow_status", {
                "workflow_states": old_doc.workflow_state,
                "approved_by": frappe.session.user,
                "approved_by_name": user_doc.full_name,
                "date": current_date
            })
        else:
            frappe.throw(f"{doc.custom_current_workflow_state}")
            doc.append("custom_workflow_status", {
                "workflow_states": "Transfer Approved",
                "approved_by": frappe.session.user,
                "approved_by_name": user_doc.full_name,
                "date": current_date
            })