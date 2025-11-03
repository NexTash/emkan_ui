import frappe
from datetime import datetime
import frappe
from frappe.utils import strip_html, nowdate
from frappe import _ 
from frappe.desk.form.assign_to import get, format_message_for_assign_to
from frappe.desk.form.document_follow import follow_document


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
import frappe

def send_workflow_email(doc, method=None):
    """
    Sends workflow email based on workflow_state.
    - For mapped workflow states, email assigned users whose ToDo.role matches.
    - For workflow_state = 'Draft', email all reviewers from 'HR Leave Review' where enable=1.
    - Skips when workflow_state = 'COO Approval'.
    """

    # --- 1️⃣ Only trigger when workflow_state changes ---
    if not doc.has_value_changed("workflow_state"):
        return

    current_state = doc.workflow_state

    # --- 2️⃣ Handle special case: Draft ---
    if current_state == "Draft":
        frappe.logger().info(f"🟦 Workflow in Draft: sending to HR Leave Reviewers")

        # Fetch all enabled reviewers
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
        return  # ✅ stop further workflow-specific processing

    # --- 3️⃣ Skip if state is 'COO Approval' ---
    if current_state == "COO Approval":
        frappe.logger().info(f"🚫 Skipping email for COO Approval on {doc.name}")
        return

    # --- 4️⃣ Map workflow state → required ToDo.role value ---
    role_mapping = {
        "Line Manager Approval": "Line Manager",
        "Division Head Approval": "HR LEAVE DIVISION HD",
        "HR Manager Approval": "HR Manager",
    }

    required_role = role_mapping.get(current_state)
    if not required_role:
        frappe.logger().info(f"⚠️ No role mapping for workflow state '{current_state}'")
        return

    # --- 5️⃣ Get assigned ToDo entries for this document ---
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

    # --- 6️⃣ Filter recipients by matching role in ToDo ---
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

    # --- 7️⃣ Compose and send email ---
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
    )

    frappe.logger().info(
        f"✅ Workflow email sent to {recipients} for {doc.name} (role={required_role})"
    )

import frappe
from frappe.utils import nowdate, strip_html, now_datetime
from frappe.desk.form.assign_to import get
from frappe.desk.form.utils import follow_document
from frappe import _
from frappe.share import add as share_add


@frappe.whitelist()
def add(args=None, *, ignore_permissions=False):
    """Add in someone's ToDo list — no assignment email."""
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

        # Update assigned_to field
        if frappe.get_meta(args["doctype"]).get_field("assigned_to"):
            frappe.db.set_value(args["doctype"], args["name"], "assigned_to", assign_to)

        doc = frappe.get_doc(args["doctype"], args["name"])

        # Share document if needed
        if not frappe.has_permission(doc=doc, user=assign_to):
            if frappe.get_system_settings("disable_document_sharing"):
                frappe.throw(_("User {0} cannot access document").format(assign_to))
            else:
                share_add(doc.doctype, doc.name, assign_to)
                shared_with_users.append(assign_to)

        # Follow document (no email)
        if frappe.get_cached_value("User", assign_to, "follow_assigned_documents"):
            follow_document(args["doctype"], args["name"], assign_to)

        # 🚫 Removed notify_assignment()

    if shared_with_users:
        user_list = ", ".join(shared_with_users)
        frappe.msgprint(_("Shared with: {0}").format(user_list))

    if users_with_duplicate_todo:
        user_list = ", ".join(users_with_duplicate_todo)
        frappe.msgprint(_("Already in ToDo: {0}").format(user_list))

    return get(args)


@frappe.whitelist()
def remove(doctype, name, assign_to):
    """Remove assignment — no unassignment email."""
    todos = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": doctype,
            "reference_name": name,
            "allocated_to": assign_to,
            "status": "Open",
        },
    )

    for todo in todos:
        todo_doc = frappe.get_doc("ToDo", todo.name)
        todo_doc.status = "Cancelled"
        todo_doc.completed_on = now_datetime()
        todo_doc.save(ignore_permissions=True)

    # 🚫 Removed notify_assignment_removed()

    frappe.msgprint(_("Assignment removed for user {0}").format(assign_to))
    return get({"doctype": doctype, "name": name})


