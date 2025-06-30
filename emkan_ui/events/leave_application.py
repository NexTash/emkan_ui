import frappe
from datetime import datetime


def clear_child_table_on_creation(doc, method=None):
    if doc.__islocal:
        doc.custom_workflow_status = []

def add_workflow_status(doc, method=None):
    current_date = datetime.now().date()
    user_doc = frappe.get_doc("User", frappe.session.user)

    old_doc = doc.get_doc_before_save()

    if old_doc is None or (doc.workflow_state != old_doc.workflow_state):
        doc.custom_current_workflow_state = doc.workflow_state

        doc.append("custom_workflow_status", {
            "workflow_states": doc.workflow_state,
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