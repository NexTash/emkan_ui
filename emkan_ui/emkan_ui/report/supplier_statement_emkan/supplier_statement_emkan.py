import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": "Date",
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 120
        },
        {
            "label": "Supplier Name",
            "fieldname": "supplier_name",
            "fieldtype": "Data",
            "width": 220
        },
        {
            "label": "Supplier Invoice No",
            "fieldname": "supplier_invoice_no",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Transaction Type",
            "fieldname": "transaction_type",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": "Document No",
            "fieldname": "document_no",
            "fieldtype": "Dynamic Link",
            "options": "transaction_type",
            "width": 180
        },
        {
            "label": "Debit",
            "fieldname": "debit",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": "Credit",
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": "Running Balance",
            "fieldname": "running_balance",
            "fieldtype": "Currency",
            "width": 150
        }
    ]


def get_data(filters):

    conditions = ""

    if filters.get("supplier"):
        conditions += " AND gl.party = %(supplier)s "

    query = f"""

    WITH supplier_statement AS
    (
        SELECT

            gl.party AS supplier,

            gl.posting_date,

            MAX(sup.supplier_name) AS supplier_name,

            gl.voucher_type,

            gl.voucher_no,

            MAX(
                CASE
                    WHEN gl.voucher_type = 'Purchase Invoice'
                    THEN pi.bill_no
                    ELSE ''
                END
            ) AS supplier_invoice_no,

            SUM(IFNULL(gl.debit,0)) AS total_debit,

            SUM(IFNULL(gl.credit,0)) AS total_credit,

            SUM(IFNULL(gl.debit,0) - IFNULL(gl.credit,0))
                AS net_amount,

            MIN(gl.creation) AS creation_time

        FROM `tabGL Entry` gl

        LEFT JOIN `tabSupplier` sup
            ON sup.name = gl.party

        LEFT JOIN `tabPurchase Invoice` pi
            ON pi.name = gl.voucher_no
           AND gl.voucher_type = 'Purchase Invoice'

        WHERE
                gl.party_type = 'Supplier'

            AND IFNULL(gl.is_cancelled,0) = 0

            AND gl.voucher_type IN
            (
                'Purchase Invoice',
                'Payment Entry',
                'Journal Entry'
            )

            {conditions}

        GROUP BY
            gl.party,
            gl.posting_date,
            gl.voucher_type,
            gl.voucher_no

        HAVING net_amount <> 0
    ),

    opening_balance AS
    (
        SELECT

            supplier,

            MAX(supplier_name) AS supplier_name,

            SUM(net_amount) AS opening_balance

        FROM supplier_statement

        WHERE posting_date < %(from_date)s

        GROUP BY supplier
    ),

    period_transactions AS
    (
        SELECT *

        FROM supplier_statement

        WHERE posting_date BETWEEN %(from_date)s AND %(to_date)s
    )

    SELECT *
    FROM
    (

        SELECT

            %(from_date)s AS date,

            ob.supplier AS supplier,

            ob.supplier_name AS supplier_name,

            'OPENING' AS supplier_invoice_no,

            '' AS transaction_type,

            '' AS document_no,

            CASE
                WHEN ob.opening_balance > 0
                THEN ob.opening_balance
                ELSE 0
            END AS debit,

            CASE
                WHEN ob.opening_balance < 0
                THEN ABS(ob.opening_balance)
                ELSE 0
            END AS credit,

            ob.opening_balance AS running_balance,

            0 AS sort_order,

            NULL AS creation_time

        FROM opening_balance ob

        UNION ALL

        SELECT

            pt.posting_date AS date,

            pt.supplier AS supplier,

            pt.supplier_name AS supplier_name,

            pt.supplier_invoice_no AS supplier_invoice_no,

            pt.voucher_type AS transaction_type,

            pt.voucher_no AS document_no,

            CASE
                WHEN pt.net_amount > 0
                THEN pt.net_amount
                ELSE 0
            END AS debit,

            CASE
                WHEN pt.net_amount < 0
                THEN ABS(pt.net_amount)
                ELSE 0
            END AS credit,

            (
                IFNULL(ob.opening_balance,0)

                +

                SUM(pt.net_amount)
                OVER
                (
                    PARTITION BY pt.supplier
                    ORDER BY
                        pt.posting_date,
                        pt.creation_time,
                        pt.voucher_no
                )
            ) AS running_balance,

            1 AS sort_order,

            pt.creation_time

        FROM period_transactions pt

        LEFT JOIN opening_balance ob
            ON ob.supplier = pt.supplier

    ) x

    ORDER BY
        x.supplier,
        x.sort_order,
        x.date,
        x.creation_time,
        x.document_no

    """

    return frappe.db.sql(query, filters, as_dict=True)