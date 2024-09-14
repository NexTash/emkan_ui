import frappe


def store_data(doc, method=None):
    timestamp = frappe.utils.now()
    doc.custom_current_workflow_state = doc.workflow_state
    old_doc = doc.get_doc_before_save()

    state_exists = False

    for row in doc.custom_workflow_status:
        if row.workflow_states == doc.workflow_state:
            row.approved_by = frappe.session.user
            state_exists = True
            break

    if doc.workflow_state == "MR Prepared":
        doc.custom_workflow_status = []
        if not doc.get("__islocal"):
            current_log = doc.get('custom_workflow_log')
            my_log = f"{timestamp} - {frappe.session.user} from {old_doc.workflow_state} to MR Prepared"
            updated_log = f"{current_log}\n{my_log}"
            doc.set('custom_workflow_log', updated_log)
        return
    
    if not state_exists:
        doc.append("custom_workflow_status", {
            "workflow_states": old_doc.workflow_state,
            "approved_by": frappe.session.user
        })
    else:
        doc.append("custom_workflow_status", {
            "workflow_states": doc.workflow_state,
            "approved_by": frappe.session.user
        })




    #Server Script by MZH
    # Ensure the custom workflow log field is initialized
    if not doc.get('custom_workflow_log'):
        doc.set('custom_workflow_log', "")

    # Get the current date and time

    if old_doc:
        workflow_entry = f"{timestamp} - {frappe.session.user} from {old_doc.workflow_state} to {doc.workflow_state}"
    else:
        workflow_entry = f"{timestamp} - {frappe.session.user} to {doc.workflow_state}"
    # Retrieve the existing workflow log
    current_log = doc.get('custom_workflow_log')

    # Append the new entry to the existing log
    if current_log:
        updated_log = f"{current_log}\n{workflow_entry}"
    else:
        updated_log = workflow_entry

    # Update the custom workflow log field
    doc.set('custom_workflow_log', updated_log)



def last_state(doc, method=None):
    # if doc.workflow_state == "COO Approved"
    doc.custom_current_workflow_state = doc.workflow_state
    doc.append("custom_workflow_status", {
            "workflow_states": "COO Approved",
            "approved_by": frappe.session.user
        })
    old_doc = doc.get_doc_before_save()
    current_log = doc.get('custom_workflow_log')
    timestamp = frappe.utils.now()
    workflow_entry = f"{timestamp} - {frappe.session.user} from {old_doc.workflow_state} to {doc.workflow_state}"
    updated_log = f"{current_log}\n{workflow_entry}"
    doc.set('custom_workflow_log', updated_log)