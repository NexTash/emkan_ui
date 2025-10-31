import frappe
from datetime import datetime
from frappe.utils import getdate, date_diff, flt
from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on, LeaveApplication
from frappe.utils import strip_html, nowdate
from frappe import _
from frappe.desk.form.assign_to import notify_assignment, get, format_message_for_assign_to
from frappe.desk.form.document_follow import follow_document

def custom_validate(doc, method):
    end_date = getdate(doc.from_date)
    forecasted_balance = get_forecasted_leave_balance(doc, doc.employee, doc.employee_name, end_date)
    total_leave_days = doc.total_leave_days or date_diff(doc.to_date, doc.from_date) + 1
    if total_leave_days > forecasted_balance:
        frappe.throw(f"Cannot apply for {total_leave_days} days. Forecasted balance by {doc.to_date} is only {forecasted_balance:.2f} days.")

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

def custom_show_insufficient_balance_message(self, leave_balance_for_consumption: float) -> None:
    if frappe.db.get_value("Leave Type", self.leave_type, "allow_negative"):
        msg = ("Warning: Insufficient leave balance for Leave Type {0}. You can still apply for leaves.").format(
            frappe.bold(self.leave_type)
        )
    else:
        msg = ("Insufficient leave balance for Leave Type {0}.").format(
            frappe.bold(self.leave_type)
        )

    frappe.msgprint(msg, title=("Leave Balance Warning"), indicator="orange")

LeaveApplication.show_insufficient_balance_message = custom_show_insufficient_balance_message


def clear_child_table_on_creation(doc, method=None):
    if doc.__islocal:
        doc.custom_workflow_status = []


def add_workflow_status(doc, method=None):
    old_doc = doc.get_doc_before_save()

    if not old_doc:
        return

    if doc.workflow_state != old_doc.workflow_state:
        previous_state = old_doc.workflow_state
        current_state = doc.workflow_state

        if current_state == "Draft":
            doc.custom_workflow_status = []
            return 

        if current_state == "Rejected":
            return

        user_doc = frappe.get_doc("User", frappe.session.user)
        current_date = datetime.now().date()

        doc.custom_current_workflow_state = current_state
        doc.append("custom_workflow_status", {
            "workflow_states": previous_state,
            "approved_by": frappe.session.user,
            "approved_by_name": user_doc.full_name,
            "date": current_date
        })


def last_state(doc, method=None):
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)
    current_date = datetime.now().date()

    if old_doc and doc.workflow_state != old_doc.workflow_state:
        doc.custom_current_workflow_state = doc.workflow_state

        doc.append("custom_workflow_status", {
            "workflow_states": doc.workflow_state,
            "approved_by": frappe.session.user,
            "approved_by_name": user_doc.full_name,
            "date": current_date
        })

def send_workflow_email(doc, method=None):
    """
    Sends workflow email based on workflow_state.
    - For mapped workflow states, email assigned users whose ToDo.role matches.
    - For workflow_state = 'Draft', email all reviewers from 'HR Leave Review' where enable=1.
    - Skips when workflow_state = 'COO Approval'.
    """

    if not doc.has_value_changed("workflow_state"):
        return

    current_state = doc.workflow_state

    if current_state == "Draft":
        frappe.logger().info(f"🟦 Workflow in Draft: sending to HR Leave Reviewers")

        reviewers = frappe.get_all(
            "HR Leave Review",
            filters={"enable": 1},
            fields=["reviewer"]
        )

        if not reviewers:
            frappe.logger().info("⚠️ No enabled reviewers found in HR Leave Review")
            return

        recipients = [r["reviewer"] for r in reviewers if r.get("reviewer")]

        if not recipients:
            frappe.logger().info("⚠️ No reviewer emails found in enabled HR Leave Review records")
            return

        subject = f"{doc.doctype} {doc.name} is now in Draft state"
        message = f"""
            <p>Dear Reviewer,</p>
            <p>The document <b>{doc.name}</b> is currently in workflow state: <b>Draft</b>.</p>
            <p>Please review the document as per your role.</p>
        """

        frappe.sendmail(
            recipients=recipients,
            subject=subject,
            message=message,
            send_after=None,
            now=True
        )

        frappe.logger().info(f"📨 Draft state email sent to HR Leave Review reviewers: {recipients}")
        return

    if current_state == "COO Approval":
        frappe.logger().info(f"🚫 Skipping email for COO Approval on {doc.name}")
        return

    role_mapping = {
        "Line Manager Approval": "Line Manager",
        "Division Head Approval": "HR LEAVE DIVISION HD",
        "HR Manager Approval": "HR Manager",
    }

    required_role = role_mapping.get(current_state)
    if not required_role:
        frappe.logger().info(f"⚠️ No role mapping for workflow state '{current_state}'")
        return

    todos = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": doc.doctype,
            "reference_name": doc.name,
            "status": "Open",
        },
        fields=["allocated_to", "role"],
    )

    if not todos:
        frappe.logger().info(f"📭 No open ToDo found for {doc.name}")
        return

    recipients = [
        todo["allocated_to"]
        for todo in todos
        if todo.get("role") == required_role
    ]

    if not recipients:
        frappe.logger().info(
            f"⚙️ No assigned user with ToDo.role='{required_role}' for {doc.name}"
        )
        return

    subject = f"{doc.doctype} {doc.name} requires your action"
    message = f"""
        <p>Dear {required_role},</p>
        <p>The document <b>{doc.name}</b> is now in workflow state: <b>{current_state}</b>.</p>
        <p>Please review and take the required action.</p>
    """

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=message,
        send_after=None,
        now=True
    )

    frappe.logger().info(
        f"✅ Workflow email sent to {recipients} for {doc.name} (role={required_role})"
    )


@frappe.whitelist()
def add(args=None, *, ignore_permissions=False):
    """Add in someone's to-do list (customized to include role field)."""

    if not args:
        args = frappe.local.form_dict

    users_with_duplicate_todo = []
    shared_with_users = []

    role_value = args.get("role") or None
    frappe.logger().info(f"🎯 Role received for assignment: {role_value}")

    assign_to_list = frappe.parse_json(args.get("assign_to")) or []

    for assign_to in assign_to_list:
        filters = {
            "reference_type": args["doctype"],
            "reference_name": args["name"],
            "status": "Open",
            "allocated_to": assign_to,
        }

        if not ignore_permissions:
            frappe.get_doc(args["doctype"], args["name"]).check_permission()

        if frappe.get_all("ToDo", filters=filters):
            users_with_duplicate_todo.append(assign_to)
            continue

        description = args.get("description") or ""
        has_content = strip_html(description) or "<img" in description
        if not has_content:
            args["description"] = _("Assignment for {0} {1}").format(args["doctype"], args["name"])

        todo_doc = frappe.get_doc({
            "doctype": "ToDo",
            "allocated_to": assign_to,
            "reference_type": args["doctype"],
            "reference_name": str(args["name"]),
            "description": args.get("description"),
            "priority": args.get("priority", "Medium"),
            "status": "Open",
            "date": args.get("date", nowdate()),
            "assigned_by": args.get("assigned_by", frappe.session.user),
            "assignment_rule": args.get("assignment_rule"),
            "role": role_value,
        }).insert(ignore_permissions=True)

        if frappe.get_meta(args["doctype"]).get_field("assigned_to"):
            frappe.db.set_value(args["doctype"], args["name"], "assigned_to", assign_to)

        doc = frappe.get_doc(args["doctype"], args["name"])

        if not frappe.has_permission(doc=doc, user=assign_to):
            if frappe.get_system_settings("disable_document_sharing"):
                msg = _("User {0} is not permitted to access this document.").format(frappe.bold(assign_to))
                msg += "<br>" + _("As document sharing is disabled, please give them the required permissions before assigning.")
                frappe.throw(msg, title=_("Missing Permission"))
            else:
                frappe.share.add(doc.doctype, doc.name, assign_to)
                shared_with_users.append(assign_to)

        if frappe.get_cached_value("User", assign_to, "follow_assigned_documents"):
            follow_document(args["doctype"], args["name"], assign_to)

        notify_assignment(
            todo_doc.assigned_by,
            todo_doc.allocated_to,
            todo_doc.reference_type,
            todo_doc.reference_name,
            action="ASSIGN",
            description=args.get("description"),
        )

    if shared_with_users:
        user_list = format_message_for_assign_to(shared_with_users)
        frappe.msgprint(_("Shared with the following Users with Read access:{0}").format(user_list), alert=True)

    if users_with_duplicate_todo:
        user_list = format_message_for_assign_to(users_with_duplicate_todo)
        frappe.msgprint(_("Already in the following Users ToDo list:{0}").format(user_list), alert=True)

    return get(args)
