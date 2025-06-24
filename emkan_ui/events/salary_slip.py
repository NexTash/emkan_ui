
import frappe
from frappe.utils import getdate

@frappe.whitelist()
def get_encashment_leave(employee):
    leave = frappe.get_all("Leave Application",
        filters={
            "employee": employee,
            "status": "Approved",
            "leave_type": "Annual Leave (Encashment)"
        },
        fields=["from_date", "to_date", "total_leave_days"],
        order_by="creation desc",
        limit=1
    )

    if leave:
        return {
            "from_date": leave[0].from_date,
            "to_date": leave[0].to_date,
            "total_leave_days": leave[0].total_leave_days
        }

    return {}
