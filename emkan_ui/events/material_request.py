import frappe
from datetime import datetime

def change_state(doc=None, method=None):
    current_date = datetime.today()
    schedule_date = datetime.strptime(str(doc.schedule_date), "%Y-%m-%d")
    current_date = datetime.now()
    if schedule_date <= current_date:
        if doc.workflow_state == "Mgmt Approved":
            frappe.db.set_value(doc.doctype, doc.name, 'workflow_state', 'Move to Purchase')
    
    frappe.db.commit()

# def assign_user(doc=None, method=None):
#     for row in 