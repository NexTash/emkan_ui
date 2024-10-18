import frappe
from datetime import datetime
from frappe.desk.form.assign_to import add

def change_state(doc=None, method=None):
    current_date = datetime.today()
    schedule_date = datetime.strptime(str(doc.schedule_date), "%Y-%m-%d")
    current_date = datetime.now()
    if schedule_date <= current_date:
        if doc.workflow_state == "Mgmt Approved":
            frappe.db.set_value(doc.doctype, doc.name, 'workflow_state', 'Move to Purchase')
    
    frappe.db.commit()

def assign_user(doc=None, method=None):
    doc = doc.as_dict()
    assign_docs = frappe.get_all("Assignment Rule Emkan", {"doctypes": doc["doctype"]}, ['*'])
    for row in assign_docs:
        my_condition =  eval(row['conditions'], {}, {"doc": doc})
        if my_condition == True:
            assign_doc = frappe.get_doc("Assignment Rule Emkan", row.name)
            for child in assign_doc.emkan_assignment_rule_users:
    
                share_doc=frappe.get_doc("DocShare", {"share_doctype":doc.doctype, "user":child.user})
                share_doc.write=child.write
                share_doc.read=child.read
                share_doc.save()
                frappe.db.commit()
                if(frappe.db.exists("ToDo", {"status" : ["!=", "Cancelled"], "allocated_to": child.user, "reference_name" : doc.name, "reference_type" : doc.doctype})):
                    continue
                add(
                    {
                        "assign_to": [child.user],
                        "doctype": doc.doctype,
                        "name": doc.name,
                        "description": "Test Assignment",
                    }
                )
                share_doc=frappe.get_doc("DocShare", {"share_doctype":doc.doctype, "user":child.user})
                share_doc.write=child.write
                share_doc.read=child.read
                share_doc.save()
                frappe.db.commit()
