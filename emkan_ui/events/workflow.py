import frappe
from datetime import datetime

def store_data(doc, method=None):
    # Get the current timestamp
    timestamp = frappe.utils.now()
    current_date = datetime.now().date()
    # Get the current workflow state and the previous state
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)
    # Proceed only if there is a change in workflow_state
    if old_doc and doc.workflow_state != old_doc.workflow_state:
        # Store the current workflow state in the custom field
        doc.custom_current_workflow_state = doc.workflow_state

        # Check if the workflow state already exists in the child table
        state_exists = False
        for row in doc.custom_workflow_status:
            if row.workflow_states == doc.workflow_state:
                row.approved_by = frappe.session.user
                row.approved_by_name = user_doc.full_name
                row.date = current_date
                state_exists = True
                break

        # Clear the custom workflow status if workflow state is "MR Prepared"
        if doc.workflow_state == "MR Prepared":
            doc.custom_workflow_status = []
            if not doc.get("__islocal"):
                # Log the transition to MR Prepared
                current_log = doc.get('custom_workflow_log')
                my_log = f"{timestamp} - {frappe.session.user} from {old_doc.workflow_state} to MR Prepared"
                updated_log = f"{current_log}\n{my_log}" if current_log else my_log
                doc.set('custom_workflow_log', updated_log)
            return
        
        # Append the old and new workflow states to the child table
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

        # Ensure the custom workflow log field is initialized
        if not doc.get('custom_workflow_log'):
            doc.set('custom_workflow_log', "")

        # Log the workflow transition
        if old_doc:
            workflow_entry = f"{timestamp} - {frappe.session.user} from {old_doc.workflow_state} to {doc.workflow_state}"
        else:
            workflow_entry = f"{timestamp} - {frappe.session.user} to {doc.workflow_state}"
        
        # Retrieve the existing workflow log
        current_log = doc.get('custom_workflow_log')

        # Append the new entry to the existing log
        updated_log = f"{current_log}\n{workflow_entry}" if current_log else workflow_entry

        # Update the custom workflow log field
        doc.set('custom_workflow_log', updated_log)

def last_state(doc, method=None):
    # Get the previous document
    old_doc = doc.get_doc_before_save()
    user_doc = frappe.get_doc("User", frappe.session.user)
    current_date = datetime.now().date()

    # Proceed only if there is a change in workflow_state
    if old_doc and doc.workflow_state != old_doc.workflow_state:
        # Set the custom current workflow state
        doc.custom_current_workflow_state = doc.workflow_state

        # Append COO Approved status to the child table
        doc.append("custom_workflow_status", {
            "workflow_states": "COO Approved",
            "approved_by": frappe.session.user,
            "approved_by_name" : user_doc.full_name,
            "date" : current_date
        })

        # Log the workflow transition
        current_log = doc.get('custom_workflow_log')
        timestamp = frappe.utils.now()
        workflow_entry = f"{timestamp} - {frappe.session.user} from {old_doc.workflow_state} to {doc.workflow_state}"
        updated_log = f"{current_log}\n{workflow_entry}" if current_log else workflow_entry
        doc.set('custom_workflow_log', updated_log)
