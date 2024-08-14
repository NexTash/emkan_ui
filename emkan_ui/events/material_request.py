import frappe
from datetime import datetime
from frappe.desk.form.assign_to import add

def assign_user(doc=None, method=None):
    assign_docs = frappe.get_all("Emkan Assignment Rule", {"doctypes": doc.doctype, "condition_key": ["!=", ""],"condition_value": ["!=", ""]}, ['name', 'condition_key', 'condition_value'])
    for row in assign_docs:
        if doc.get(row.condition_key) and doc.get(row.condition_key) == row.condition_value:        
            assign_doc = frappe.get_doc("Emkan Assignment Rule", row.name)
            for child in assign_doc.emkan_assignment_rule_users:
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
