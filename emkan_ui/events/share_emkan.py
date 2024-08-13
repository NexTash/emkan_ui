import frappe


def after_insert(doc, method=None):
    if doc.share_doctype == "Material Request":
        doc.read = 1
        doc.write = 1

    doc.save()
    
    frappe.db.commit()

def remove_share(doc, method=None):
    if doc.status == "Cancelled":
        frappe.db.delete("DocShare", {"share_doctype": doc.reference_type, "share_name" : doc.reference_name, "user" : doc.allocated_to})    
    frappe.db.commit()
    

