import frappe
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "date",
            "label": "Date",
            "fieldtype": "Date",
            "width": 120,
            "align": "left"
        },
        {
            "fieldname": "details",
            "label": "Reference",
            "fieldtype": "Data",
            "width": 200,
            "align": "left"
        },
        {
            "fieldname": "transactions",
            "label": "Tran Type",
            "fieldtype": "Data",
            "width": 150,
            "align": "left"
        },
        {
            "fieldname": "check_no",
            "label": "Check Ref / LPO",
            "fieldtype": "Data",
            "width": 150,
            "align": "left"
        },
        {
            "fieldname": "amount_dr",
            "label": "Debit",
            "fieldtype": "Data",
            "width": 120,
            "align": "right"
        },
        {
            "fieldname": "amount_cr",
            "label": "Credit",
            "fieldtype": "Data",
            "width": 120,
            "align": "right"
        },
        {
            "fieldname": "balance",
            "label": "Balance",
            "fieldtype": "Data",
            "width": 120,
            "align": "right"
        }
    ]

def get_opening_balance(filters):
    conditions = ""
    if filters.get("supplier"):
        conditions += " AND party = %(supplier)s"
    if filters.get("from_date"):
        conditions += " AND posting_date < %(from_date)s"

    opening_balance = frappe.db.sql(f"""
        SELECT
            SUM(debit) - SUM(credit) as opening_balance
        FROM
            `tabGL Entry`
        WHERE
            docstatus = 1
            AND party_type = 'Supplier'
            {conditions}
    """, filters, as_dict=True)

    opening_balance_value = opening_balance[0].opening_balance if opening_balance else 0
    
    if opening_balance_value is None or opening_balance_value == 0 or opening_balance_value != opening_balance_value:
        return ""
    
    return opening_balance_value

def format_currency(value):
    if value is None:
        return ""
    return "{:,.2f}".format(value) if value else ""

def get_exchange_rate(from_currency, to_currency, date):
    exchange_rate = frappe.db.get_value("Currency Exchange", 
                                        {"from_currency": from_currency, "to_currency": to_currency, "date": ["<=", date]}, 
                                        "exchange_rate")
    if not exchange_rate:
        exchange_rate = frappe.db.get_value("Currency Exchange", 
                                            {"from_currency": from_currency, "to_currency": to_currency}, 
                                            "exchange_rate")
    return flt(exchange_rate) if exchange_rate else 1.0 

def convert_currency(amount, from_currency, to_currency, date):
    if from_currency == to_currency:
        return amount
    exchange_rate = get_exchange_rate(from_currency, to_currency, date)
    return amount / exchange_rate

def get_data(filters):
    default_currency = frappe.get_value("Company", filters.get("company"), "default_currency")
    opening_balance = get_opening_balance(filters)
    previous_balance = opening_balance

    balance = previous_balance 
    total_cr = 0
    total_dt = 0

    conditions = ""
    if filters.get("supplier"):
        conditions += " AND party = %(supplier)s"
    if filters.get("from_date"):
        conditions += " AND posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND posting_date <= %(to_date)s"
        
    gl_entries = frappe.db.sql(f"""
        SELECT
            posting_date,
            voucher_type,
            voucher_no,
            due_date,
            debit,
            credit,
            account_currency
        FROM
            `tabGL Entry`
        WHERE
            docstatus = 1
            AND party_type = 'Supplier'
            {conditions}
        ORDER BY
            posting_date ASC, voucher_type ASC, voucher_no ASC
    """, filters, as_dict=True)

    data = []
    processed_references = set()

    data.append({
        "date": filters.get('from_date'),
        "transactions": "",
        "details": "",
        "check_no": "Opening Balance",
        "amount_dr": "",
        "amount_cr": "",
        "balance": format_currency(opening_balance)
    })

    if filters.get("supplier"):
        supplier_currency = frappe.db.get_value("Supplier", filters.get("supplier"), ["default_currency"]) 
    if not supplier_currency:
        supplier_currency = default_currency
    counter=0
    unique={}

    for entry in gl_entries:
        transactions = ""
        details = ""
        check_no = ""
        amount_cr = entry['credit'] or 0
        amount_dr = entry['debit'] or 0

        if entry['account_currency'] and entry['account_currency'] != default_currency:
            amount_cr = convert_currency(amount_cr, entry['account_currency'], default_currency, entry['posting_date'])
            amount_dr = convert_currency(amount_dr, entry['account_currency'], default_currency, entry['posting_date'])

        if entry['voucher_no'] in processed_references and entry['voucher_type'] != "Journal Entry":
            continue

        if entry['voucher_type'] == "Purchase Invoice":
            status, is_return = frappe.db.get_value("Purchase Invoice", entry['voucher_no'], ['docstatus', 'is_return'])
            exists = frappe.db.exists("Repost Accounting Ledger Items", {"voucher_no": entry['voucher_no'], "voucher_type": "Purchase Invoice"})
            
            if status == 2:
                continue
            
            if is_return:
                transactions = f"{entry['voucher_type']} (Debit MEMO)"
            else:
                transactions = entry['voucher_type']
            
            if exists:
                transactions = f"{entry['voucher_type']}"
                if entry["debit"] > entry["credit"]:
                    amount_cr = entry["debit"]
                    amount_dr = entry["credit"]
                else:
                    amount_cr = entry["credit"]
                    amount_dr = entry["debit"]

            details = f"{entry['voucher_no']}"

        elif entry['voucher_type'] == "Payment Entry":
            pe_doc = frappe.get_doc("Payment Entry", entry['voucher_no'])
            if pe_doc.docstatus == 2:
                continue
            
            paid_amount = pe_doc.get('paid_amount', 0.0)
            transactions = entry['voucher_type']
            check_no = pe_doc.reference_no or ""
            details = f"{entry['voucher_no']}"
            amount_dr = paid_amount

        elif entry['voucher_type'] == "Journal Entry":
            je_doc = frappe.get_doc("Journal Entry", entry['voucher_no'])
            if je_doc.docstatus == 2:
                continue
            if entry['voucher_no'] not in unique:
                unique[entry['voucher_no']] = counter + 1
            else:
                entry_jv = unique[entry['voucher_no']]
                if data[entry_jv]['details'] == entry['voucher_no']:
                    data[entry_jv]['amount_dr'] = sum_values(data[entry_jv]['amount_dr'], amount_dr) 
                    data[entry_jv]['amount_cr'] = sum_values(data[entry_jv]['amount_cr'], amount_cr)
                    total_cr = sum_values(total_cr, amount_cr)
                    total_dt = sum_values(total_dt, amount_dr)
                    continue
       
            transactions = entry['voucher_type']
            details = f"{entry['voucher_no']}"
         
        total_cr += amount_cr
        total_dt += amount_dr
        balance = (previous_balance or 0) + (amount_dr - amount_cr)

        data.append({
            "date": entry['posting_date'],
            "transactions": transactions,
            "details": details,
            "check_no": check_no,
            "amount_dr": format_currency(amount_dr),
            "amount_cr": format_currency(amount_cr),
            "balance": format_currency(balance)
        })
 
        previous_balance = balance
        processed_references.add(entry['voucher_no'])
        counter += 1

    data.append({
        "details": "",
        "check_no": "Total :",
        "amount_dr": format_currency(total_dt),
        "amount_cr": format_currency(total_cr),
        "balance": format_currency(balance)
    })

    return data

def sum_values(value1, value2):
    # Helper function to convert string to float
    def to_float(value):
        if isinstance(value, str):
            # Remove commas and check for empty strings
            value = value.replace(',', '').strip()
            if value == '':
                return 0.0  # Return 0.0 for empty strings
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0  # Handle invalid values by returning 0.0

    # Convert both values to float and return their sum
    return to_float(value1) + to_float(value2)
