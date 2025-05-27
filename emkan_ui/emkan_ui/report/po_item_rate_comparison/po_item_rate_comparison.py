# Copyright (c) 2025, NexTash and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data"},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data"},
        {"label": "Current PO", "fieldname": "current_po", "fieldtype": "Data"},
        {"label": "Last PO", "fieldname": "last_po", "fieldtype": "Data"},
        {"label": "2nd Last PO", "fieldname": "second_last_po", "fieldtype": "Data"},
        {"label": "3rd Last PO", "fieldname": "third_last_po", "fieldtype": "Data"},
        {"label": "4th Last PO", "fieldname": "fourth_last_po", "fieldtype": "Data"}
    ]

    if not filters.po_number:
        return columns, []

    items = frappe.db.get_all(
        'Purchase Order Item',
        filters={"parent": filters.po_number},
        fields=["item_code", "item_name", "rate", "uom", "parent", "schedule_date"]
    )

    data = []

    for item in items:
        history = frappe.db.sql("""
            SELECT poi.parent, po.transaction_date, poi.rate, po.currency, poi.uom
            FROM `tabPurchase Order Item` poi
            JOIN `tabPurchase Order` po ON poi.parent = po.name
            WHERE poi.item_code = %s
              AND po.docstatus = 1
              AND poi.parent != %s
            ORDER BY po.transaction_date DESC
            LIMIT 4
        """, (item.item_code, filters.po_number), as_dict=True)

        formatted = lambda row: f"{row.parent} / {row.transaction_date} / {row.rate:.2f} / {row.currency} / {row.uom}" if row else ""

        row = {
            "item_code": item.item_code,
            "item_name": item.item_name,
            "current_po": f"{item.parent} / {item.schedule_date} / {item.rate:.2f} / {frappe.db.get_value('Purchase Order', item.parent, 'currency')} / {item.uom}",
            "last_po": formatted(history[0]) if len(history) > 0 else "",
            "second_last_po": formatted(history[1]) if len(history) > 1 else "",
            "third_last_po": formatted(history[2]) if len(history) > 2 else "",
            "fourth_last_po": formatted(history[3]) if len(history) > 3 else "",
        }

        data.append(row)

    return columns, data
