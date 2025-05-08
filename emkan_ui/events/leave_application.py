
import frappe
from datetime import datetime

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