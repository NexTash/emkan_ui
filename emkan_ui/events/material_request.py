import frappe
from datetime import datetime
from frappe.utils import nowdate, now_datetime, strip_html
from frappe.desk.form.assign_to import add, remove
from frappe import _
from frappe.desk.form.utils import follow_document
from frappe.share import add as share_add
from frappe.desk.form.assign_to import get


def change_state(doc=None, method=None):
    
    current_date = datetime.now()
    schedule_date = datetime.strptime(str(doc.schedule_date), "%Y-%m-%d")

    if schedule_date <= current_date:
        if doc.workflow_state == "Mgmt Approved":
            frappe.db.set_value(doc.doctype, doc.name, "workflow_state", "Move to Purchase")
    frappe.db.commit()


def assign_user(doc=None, method=None):

    doc = doc.as_dict()
    assign_rules = frappe.get_all("Assignment Rule Emkan", {"doctypes": doc["doctype"]}, ["*"])
    for rule in assign_rules:
        if not eval(rule["conditions"], {}, {"doc": doc}):
            continue

        assign_doc = frappe.get_doc("Assignment Rule Emkan", rule.name)
        for child in assign_doc.emkan_assignment_rule_users:
            existing_share = frappe.get_all(
                "DocShare", filters={"share_doctype": doc.doctype, "user": child.user}, limit=1
            )
            if existing_share:
                share_doc = frappe.get_doc("DocShare", existing_share[0].name)
            else:
                share_doc = frappe.new_doc("DocShare")
                share_doc.share_doctype = doc.doctype
                share_doc.share_name = doc.name
                share_doc.user = child.user

            share_doc.write = child.write
            share_doc.read = child.read
            share_doc.submit = child.submit_
            share_doc.share = child.share
            share_doc.flags.ignore_share_permission = True
            share_doc.save(ignore_permissions=True)

            if frappe.db.exists(
                "ToDo",
                {
                    "status": ["!=", "Cancelled"],
                    "allocated_to": child.user,
                    "reference_name": doc.name,
                    "reference_type": doc.doctype,
                },
            ):
                continue

            add_assignment_silent(
                {
                    "assign_to": [child.user],
                    "doctype": doc.doctype,
                    "name": doc.name,
                    "description": "Test Assignment",
                }
            )

            frappe.db.commit()

@frappe.whitelist()
def add_assignment_silent(args=None, *, ignore_permissions=False): 

    original_notify = add
    original_notify_removed = remove
    frappe.desk.form.assign_to.add = lambda *a, **k: None
    frappe.desk.form.assign_to.remove = lambda *a, **k: None

    try:
        if not args:
            args = frappe.local.form_dict

        assign_to_list = frappe.parse_json(args.get("assign_to")) or []
        users_with_duplicate_todo = []
        shared_with_users = []

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

            todo_doc = frappe.get_doc(
                {
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
                }
            ).insert(ignore_permissions=True)

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

    finally:
        frappe.desk.form.assign_to.add = original_notify
        frappe.desk.form.assign_to.remove = original_notify_removed


@frappe.whitelist()
def remove_assignment_silent(doctype, name, assign_to):

    original_notify_removed = remove
    frappe.desk.form.assign_to.remove = lambda *a, **k: None

    try:
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

        frappe.msgprint(_("Assignment removed for user {0}").format(assign_to))
        return get({"doctype": doctype, "name": name})

    finally:
        frappe.desk.form.assign_to.remove = original_notify_removed
