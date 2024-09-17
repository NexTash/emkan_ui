import frappe

def delete_assigned(doc=None, method=None):
    if doc.reference_doctype == "Material Request" and doc.comment_type == "Assigned":
        doc.delete()

    frappe.db.commit()