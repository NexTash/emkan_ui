import frappe
from frappe.utils import today, date_diff, add_months, get_last_day

def assign_leave_policy_on_update(doc, method):
    if not doc.date_of_joining:
        return

    years = date_diff(today(), doc.date_of_joining) // 365

    if years < 1:
        title = "Annual Leave Policy - 21 Days"
    elif years < 5:
        title = "Annual Leave Policy - 25 Days"
    else:
        title = "Annual Leave Policy - 30 Days"

    policy_doc = frappe.get_value("Leave Policy", {"title": title}, "name")
    if not policy_doc:
        frappe.msgprint(f"Leave Policy with title '{title}' not found.")
        return

    existing = frappe.get_all("Leave Policy Assignment", filters={
        "employee": doc.name,
        "leave_policy": policy_doc,
        "effective_from": [">=", doc.date_of_joining]
    })

    if existing:
        frappe.msgprint(f"Leave Policy with '{title}' already assigned.")
        return  # Already assigned

    assignment = frappe.new_doc("Leave Policy Assignment")
    assignment.employee = doc.name
    assignment.leave_policy = policy_doc
    assignment.assignment_based_on = "Joining Date"
    assignment.effective_from = doc.date_of_joining
    assignment.effective_to = get_last_day(add_months(assignment.effective_from, 12))
    assignment.save(ignore_permissions=True)
    assignment.submit()

    frappe.msgprint(f"Leave policy '{title}' assigned to {doc.employee_name}.")



@frappe.whitelist()
def assign_leave_policy(employee):
    emp = frappe.get_doc("Employee", employee)
    
    if not emp.date_of_joining:
        return "Date of joining not set."

    years = date_diff(today(), emp.date_of_joining) // 365

    if years < 1:
        title = "Annual Leave Policy - 21 Days"
    elif years < 5:
        title = "Annual Leave Policy - 25 Days"
    else:
        title = "Annual Leave Policy - 30 Days"

    policy_doc = frappe.get_value("Leave Policy", {"title": title}, "name")
    if not policy_doc:
        return f"Leave Policy with title '{title}' not found."

    existing = frappe.get_all("Leave Policy Assignment", filters={
        "employee": emp.name,
        "leave_policy": policy_doc,
        "effective_from": [">=", emp.date_of_joining]
    })

    if existing:
        return "Policy already assigned."

    assignment = frappe.new_doc("Leave Policy Assignment")
    assignment.employee = emp.name
    assignment.leave_policy = policy_doc
    assignment.assignment_based_on = "Joining Date"
    assignment.effective_from = emp.date_of_joining
    assignment.effective_to = get_last_day(add_months(assignment.effective_from, 12))
    assignment.save(ignore_permissions=True)
    assignment.submit()

    return f"Leave policy '{title}' assigned to {emp.employee_name}."
