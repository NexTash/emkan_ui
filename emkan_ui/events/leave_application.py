import frappe
from datetime import datetime

def store_data(doc, method=None):
    # Get the current timestamp and user info
    current_date = datetime.now().date()
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)

    # Check if workflow state has changed
    if old_doc and doc.workflow_state != old_doc.workflow_state:
        # Clear the child table
        doc.custom_workflow_status = []

        # Update current workflow state
        doc.custom_current_workflow_state = doc.workflow_state

        # Add the new workflow state entry
        doc.append("custom_workflow_status", {
            "workflow_states": doc.workflow_state,
            "approved_by": frappe.session.user,
            "approved_by_name": user_doc.full_name,
            "date": current_date
        })

def last_state(doc, method=None):
    # Get the previous document state
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)
    current_date = datetime.now().date()

    # Proceed if there is a change in workflow_state
    if old_doc and doc.workflow_state != old_doc.workflow_state:
        # Clear the child table
        doc.custom_workflow_status = []

        # Set the custom current workflow state
        doc.custom_current_workflow_state = doc.workflow_state

        # Add the new workflow state entry
        doc.append("custom_workflow_status", {
            "workflow_states": doc.workflow_state,
            "approved_by": frappe.session.user,
            "approved_by_name": user_doc.full_name,
            "date": current_date
        })
