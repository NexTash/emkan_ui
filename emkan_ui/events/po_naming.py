import frappe
import datetime

def autoname(doc, method=None):
    current_year = datetime.datetime.now().strftime("%y")
    digits = 6
    prefix = doc.custom_prefix

    settings = frappe.get_single("PO Series counter")
    if not settings.lpo_series_counter:
        frappe.throw("Please set counter in PO Series counter")

    current_number = settings.lpo_series_counter + 1

    settings.lpo_series_counter = current_number
    settings.save()

    formatted_number = format_with_leading_zeros(current_number, digits)
    doc.name = f"{prefix}{current_year}-{formatted_number}"

def format_with_leading_zeros(number, digits):
    return str(number).zfill(digits)



@frappe.whitelist()
def rate(purchase_order_name):
    # Fetch the minimum rate from the Purchase Order Items
    min_price = frappe.db.sql("""
        SELECT MIN(rate) 
        FROM `tabPurchase Order Item` 
        WHERE parent=%s
    """, (purchase_order_name,))[0][0]

    if min_price:
        # Update all items in the Purchase Order with the minimum price
        frappe.db.sql("""
            UPDATE `tabPurchase Order Item` 
            SET custom_minimum_purchases_price = %s 
            WHERE parent = %s
        """, (min_price, purchase_order_name))

        frappe.db.commit()
        # frappe.msgprint(f"Updated custom_minimum_purchases_price to {min_price}")

# Example usage: Fetch last PO and update
last_doc = frappe.get_last_doc("Purchase Order")
rate(last_doc.name)
0
