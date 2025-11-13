import frappe
from datetime import datetime
import frappe
from frappe import _ 
from frappe.desk.form.assign_to import get, format_message_for_assign_to
from frappe.desk.form.document_follow import follow_document
from frappe.utils import nowdate, strip_html, now_datetime
from frappe.desk.form.assign_to import get
from frappe.desk.form.utils import follow_document
from frappe import _
from frappe.share import add as share_add


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
    if not doc.has_value_changed("workflow_state"):
        return

    current_state = doc.workflow_state

    leave_type = getattr(doc, "leave_type", "")
    reference_no = doc.name
    employee_id = getattr(doc, "employee", "")
    employee_name = frappe.db.get_value("Employee", employee_id, "employee_name") or ""
    doc_link = frappe.utils.get_link_to_form(doc.doctype, doc.name, label="View Document")

    if current_state == "Draft":
        reviewers = frappe.get_all(
            "HR Leave Review",
            filters={"enable": 1},
            fields=["reviewer"]
        )

        if not reviewers:
            return

        recipients = [r["reviewer"] for r in reviewers if r.get("reviewer")]
        if not recipients:
            return

        for recipient in recipients:
            recipient_full_name = frappe.db.get_value("User", recipient, "full_name") or "Reviewer"

            subject = f"{leave_type} Application for Approval – {reference_no}"
            message = f"""
                <p style='color:red;'><b>** Do Not Reply to This Email **</b></p>
                <p>Dear {recipient_full_name},</p>
                <p>
                    You are requested to review the <b>{leave_type}</b> Application 
                    (Reference No: <b>{reference_no}</b>) submitted by employee: 
                    <b>{employee_id} - {employee_name}</b>.
                </p>
                <p>Please use the link <a>{doc_link}</a> or log in to EMKAN ERP to take the necessary action.</p>
                <p>This is an automated message. Please do not reply.</p>
                <p style="font-size:12px;">#Sent from EMKAN ERP</p>
            """

            frappe.sendmail(
                recipients=[recipient],
                subject=subject,
                message=message,
                now=True
            )

        frappe.logger().info(f"📨 Draft state email sent to HR reviewers: {recipients}")
        return

    if current_state == "COO Approval":
        return

    role_mapping = {
        "Line Manager Approval": "Line Manager",
        "Division Head Approval": "HR LEAVE DIVISION HD",
        "HR Manager Approval": "HR Manager",
    }

    required_role = role_mapping.get(current_state)
    recipients = []

    if current_state == "HR Manager Approval":
        recipients = ["retheesh.k@emkanengineering.com"]
    else:
        todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": doc.doctype,
                "reference_name": doc.name,
                "status": "Open",
            },
            fields=["allocated_to", "role"],
        )

        if todos:
            recipients = [
                todo["allocated_to"]
                for todo in todos
                if todo.get("role") == required_role
            ]

    if not recipients:
        frappe.logger().warning(f"⚠️ No recipients found for workflow_state={current_state}, doc={doc.name}")
        return

    for recipient in recipients:
        recipient_full_name = frappe.db.get_value("User", recipient, "full_name") or required_role or "Approver"

        subject = f"{leave_type} Application for Approval – {reference_no}"
        message = f"""
            <p style='color:red;'><b>** Do Not Reply to This Email **</b></p>
            <p>Dear {recipient_full_name},</p>
            <p>
                You are requested to review the <b>{leave_type}</b> Application 
                (Reference No: <b>{reference_no}</b>) submitted by employee: 
                <b>{employee_id} - {employee_name}</b>.
            </p>
            <p>Please use the link <a>{doc_link}</a> or log in to EMKAN ERP to take the necessary action.</p>
            <p>This is an automated message. Please do not reply.</p>
            <p style="font-size:12px;">#Sent from EMKAN ERP</p>
        """

        try:
            frappe.sendmail(
                recipients=[recipient],
                subject=subject,
                message=message,
                now=True
            )
            frappe.logger().info(f"✅ Email sent to {recipient} for state={current_state}")
        except Exception as e:
            frappe.log_error(f"❌ Failed to send email to {recipient}: {e}")

    frappe.logger().info(f"📧 Workflow email successfully sent for {doc.name} ({current_state})")


@frappe.whitelist()
def add(args=None, *, ignore_permissions=False):
    if not args:
        args = frappe.local.form_dict

    users_with_duplicate_todo = []
    shared_with_users = []

    if args.get("workflow_state") == "HR Manager Approval":
        frappe.logger().info("🟡 Skipping ToDo creation for HR Manager Approval")
        return get(args)

    role_value = args.get("role") or None
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

        frappe.get_doc({
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
                frappe.throw(_("User {0} cannot access document").format(assign_to))
            else:
                share_add(doc.doctype, doc.name, assign_to)
                shared_with_users.append(assign_to)

        if frappe.get_cached_value("User", assign_to, "follow_assigned_documents"):
            follow_document(args["doctype"], args["name"], assign_to)

    if shared_with_users:
        frappe.msgprint(_("Shared with: {0}").format(", ".join(shared_with_users)))

    if users_with_duplicate_todo:
        frappe.msgprint(_("Already in ToDo: {0}").format(", ".join(users_with_duplicate_todo)))

    return get(args)


@frappe.whitelist()
def remove(doctype, name, assign_to):
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

    return get({"doctype": doctype, "name": name})