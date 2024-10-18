import frappe

@frappe.whitelist(allow_guest = True)
def mapping_cost_center(division):
    doc = frappe.get_doc("Cost Center Mapping")
    for row in doc.items:
        if division == row.division:
            return row.cost_center