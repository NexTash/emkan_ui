import frappe

def execute(filters=None):
    columns = get_columns()
    conditions = ""

    if filters.get("supplier"):
        conditions += " AND gl.party = %(supplier)s "

    data = frappe.db.sql("""
    WITH opening_balance AS
    (
        SELECT
            gl.party AS supplier,
            SUM(IFNULL(gl.debit,0))  AS opening_debit,
            SUM(IFNULL(gl.credit,0)) AS opening_credit,
            SUM(IFNULL(gl.debit,0) - IFNULL(gl.credit,0)) AS opening_balance
        FROM `tabGL Entry` gl
        WHERE
            gl.party_type = 'Supplier'
            AND gl.account IN (
                '210004 - Sundry Creditors - EECS',
                '115306 - Advances to Suppliers - EECS'
            )
            AND IFNULL(gl.is_cancelled,0) = 0
            AND gl.posting_date < %(from_date)s
            {conditions}
        GROUP BY gl.party
    ),

    transaction_data AS
    (
        SELECT
            MAX(gl.posting_date)                               AS posting_date,
            gl.party                                           AS supplier,
            sup.supplier_name                                  AS supplier_name,
            CASE
                WHEN gl.voucher_type = 'Purchase Invoice'
                THEN pi.bill_no
                ELSE ''
            END                                                AS supplier_invoice_no,
            gl.voucher_type                                    AS voucher_type,
            gl.voucher_no                                      AS voucher_no,
            SUM(IFNULL(gl.debit,0))                            AS debit,
            SUM(IFNULL(gl.credit,0))                           AS credit,
            /* Summing net balance for the specific voucher to group duplicates */
            SUM(IFNULL(gl.debit,0) - IFNULL(gl.credit,0))      AS balance,
            MIN(gl.creation)                                   AS creation_time
        FROM `tabGL Entry` gl
        LEFT JOIN `tabSupplier` sup
            ON sup.name = gl.party
        LEFT JOIN `tabPurchase Invoice` pi
            ON pi.name = gl.voucher_no
            AND gl.voucher_type = 'Purchase Invoice'
        WHERE
            gl.party_type = 'Supplier'
            AND gl.account IN (
                '210004 - Sundry Creditors - EECS',
                '115306 - Advances to Suppliers - EECS'
            )
            AND IFNULL(gl.is_cancelled,0) = 0
            AND gl.voucher_type IN (
                'Purchase Invoice',
                'Payment Entry',
                'Journal Entry'
            )
            AND gl.posting_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}
        GROUP BY
            gl.party,
            gl.voucher_type,
            gl.voucher_no
    ),

    running_transactions AS
    (
        SELECT
            td.*,
            (
                IFNULL(ob.opening_balance,0)
                +
                SUM(td.balance)
                OVER
                (
                    PARTITION BY td.supplier
                    ORDER BY td.posting_date, td.creation_time, td.voucher_no
                )
            ) AS running_balance
        FROM transaction_data td
        LEFT JOIN opening_balance ob
            ON ob.supplier = td.supplier
    ),

    closing_balance AS
    (
        SELECT
            rt.supplier,
            MAX(rt.supplier_name) AS supplier_name,
            (
                IFNULL(ob.opening_balance,0)
                +
                SUM(rt.balance)
            ) AS closing_balance
        FROM running_transactions rt
        LEFT JOIN opening_balance ob
            ON ob.supplier = rt.supplier
        GROUP BY rt.supplier
    ),

    final_data AS
    (
        /* OPENING BALANCE ROW */
        SELECT
            ''                                                 AS posting_date,
            ''                                                 AS supplier,
            ''                                                 AS supplier_name,
            ''                                                 AS supplier_invoice_no,
            ''                                                 AS voucher_type,
            'Opening'                                          AS voucher_no,
            ob.opening_debit                                   AS debit,
            ob.opening_credit                                  AS credit,
            ob.opening_balance                                 AS running_balance,
            '0000-00-00 00:00:00'                              AS creation_time,
            0                                                  AS sort_order
        FROM opening_balance ob

        UNION ALL

        /* TRANSACTION ROWS (NOW CONSOLIDATED) */
        SELECT
            rt.posting_date,
            rt.supplier,
            rt.supplier_name,
            rt.supplier_invoice_no,
            rt.voucher_type,
            rt.voucher_no,
            rt.debit,
            rt.credit,
            rt.running_balance,
            rt.creation_time,
            1                                                  AS sort_order
        FROM running_transactions rt

        UNION ALL

        /* CLOSING BALANCE ROW */
        SELECT
            ''                                                 AS posting_date,
            ''                                                 AS supplier,
            ''                                                 AS supplier_name,
            ''                                                 AS supplier_invoice_no,
            'Closing Balance'                                  AS voucher_type,
            ''                                                 AS voucher_no,
            0                                                  AS debit,
            0                                                  AS credit,
            cb.closing_balance                                 AS running_balance,
            '9999-12-31 23:59:59'                              AS creation_time,
            2                                                  AS sort_order
        FROM closing_balance cb
    )

    SELECT
        posting_date,
        supplier,
        supplier_name,
        supplier_invoice_no,
        voucher_type,
        voucher_no,
        debit,
        credit,
        running_balance
    FROM final_data
    ORDER BY supplier, sort_order, posting_date, creation_time

    """.format(conditions=conditions), filters, as_dict=1)

    return columns, data


def get_columns():
    return [
        {
            "label": "Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 140
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
            "fieldname": "voucher_type",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": "Document No",
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
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