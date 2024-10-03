// Copyright (c) 2024, nextash.com and contributors
// For license information, please see license.txt

frappe.query_reports["Supplier Statement"] = {
    "filters": [
        {
            fieldname: "supplier",
            label: ("Supplier"),
            fieldtype: "Link",
            options: "Supplier",
            width: 100,
            reqd: 1,
            on_change: function(report) {
                let supplier = frappe.query_report.get_filter_value('supplier');
                if (supplier) {
                    frappe.db.get_doc('Supplier', supplier)
                        .then(supplier_doc => {
                            localStorage.setItem("supplier", JSON.stringify({
                                id: supplier_doc.name,
                                name: supplier_doc.supplier_name,
                            }));

                            // Handle supplier currency
                            if (supplier_doc.default_currency) {
                                localStorage.setItem("supplier_currency", JSON.stringify({
                                    currency: supplier_doc.default_currency,
                                }));
                            } else {
                                let company = frappe.query_report.get_filter_value('company');
                                if (company) {
                                    frappe.db.get_doc('Company', company)
                                        .then(company_doc => {
                                            localStorage.setItem("supplier_currency", JSON.stringify({
                                                currency: company_doc.default_currency,
                                            }));
                                        });
                                }
                            }

                            // Handle supplier primary address
                            if (supplier_doc.supplier_primary_address) {
                                frappe.db.get_doc('Address', supplier_doc.supplier_primary_address)
                                    .then(address_doc => {
                                        // Store supplier address in localStorage
                                        let address_parts = [
                                            address_doc.address_line1 || "",
                                            address_doc.address_line2 || "",
                                            address_doc.city || "",
                                            address_doc.country || ""
                                        ];
                                        let full_address = address_parts.filter(Boolean).join('<br>');
                                        localStorage.setItem("supplier_address", JSON.stringify({
                                            address: full_address
                                        }));
                                    });
                            } else {
                                localStorage.setItem("supplier_address", JSON.stringify({
                                    address: ''
                                }));
                            }

                            // Handle supplier primary contact
                            if (supplier_doc.supplier_primary_contact) {
                                frappe.db.get_doc('Contact', supplier_doc.supplier_primary_contact)
                                    .then(contact_doc => {
                                        let phone_no = "";
                                        for (let row of contact_doc.phone_nos) {
                                            if (row.is_primary_phone) {
                                                phone_no = row.phone;
                                            }
                                        }
                                        let email_id = "";
                                        for (let row of contact_doc.email_ids) {
                                            if (row.is_primary) {
                                                email_id = row.email_id;
                                            }
                                        }
                                        setTimeout(() => {
                                            localStorage.setItem("supplier_contact", JSON.stringify({
                                                phone: phone_no,
                                                email: email_id
                                            }));
                                        }, 500);
                                    });
                            } else {
                                setTimeout(() => {
                                    localStorage.setItem("supplier_contact", JSON.stringify({
                                        phone: '',
                                        email: ''
                                    }));
                                }, 500);
                            }
                        });
                } else {
                    localStorage.removeItem("supplier");
                    localStorage.removeItem("supplier_address");
                    localStorage.removeItem("supplier_contact");
                }
            }
        },
        {
            fieldname: "from_date",
            label: ("From Date"),
            fieldtype: "Date",
            width: 100,
            reqd: 0,
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            on_change: function(report) {
                let from_date = frappe.query_report.get_filter_value('from_date');
                if (from_date) {
                    localStorage.setItem("from_date", JSON.stringify({from_date}));
                } else {
                    localStorage.setItem("from_date", JSON.stringify({}));
                }
                report.refresh();
            }
        },
        {
            fieldname: "to_date",
            label: ("To Date"),
            fieldtype: "Date",
            width: 100,
            reqd: 0,
            default: frappe.datetime.get_today(),
            on_change: function(report) {
                let to_date = frappe.query_report.get_filter_value('to_date');
                if (to_date) {
                    localStorage.setItem("to_date", JSON.stringify({to_date}));
                } else {
                    localStorage.setItem("to_date", JSON.stringify({}));
                }
                report.refresh();
            }
        },
        {
            fieldname: "company",
            label: ("Company"),
            fieldtype: "Link",
            options: "Company",
            width: 100,
            reqd: 1,
            on_change: function(report) {
                let company = frappe.query_report.get_filter_value('company');
                if (company) {
                    frappe.db.get_list('Dynamic Link', {
                        filters:{
                            link_doctype: "Company",
                            link_name : company,
                            link_title: company
                        },
                        fields:['parent']
                    }).then(records => {    
                        if(records && records.length > 0){
                            let office_address = "";
                            for(let row of records){
                                frappe.db.get_doc('Address', row.parent).then(address_doc => {
                                    if(address_doc.address_type == "Office"){
                                        // Combine address fields
                                        let address_parts = [
                                            address_doc.address_line1 || "",
                                            address_doc.address_line2 || "",
                                            address_doc.city || "",
                                            address_doc.country || ""
                                        ];
                                        // Filter out any empty parts and join them with a comma
                                        office_address = address_parts.filter(Boolean).join('<br>');
                                    }
                                });
                            }
                            setTimeout(() => {
                                localStorage.setItem("company_address", JSON.stringify({
                                    address : office_address
                                }));
                            }, 2000);
                        }
                    });
                    frappe.db.get_doc('Company', company).then(company_doc => {
                        localStorage.setItem("company", JSON.stringify({
                            name: company_doc.name,
                            phone: company_doc.phone_no,
                            email: company_doc.email,
                            website: company_doc.website,
                        }));
                    });
                } else {
                    localStorage.setItem("company", JSON.stringify({}));
                    localStorage.setItem("company_address", JSON.stringify({}));
                }
                report.refresh();
            }
        },
        
        
        
    ],
    onload: function (report) {
		let to_date = frappe.query_report.get_filter_value('to_date');
        if (to_date) {
            localStorage.setItem("to_date", JSON.stringify({to_date}));
        } else {
            localStorage.setItem("to_date", JSON.stringify({}));
        }

        setTimeout(() => {
            
            localStorage.setItem("current_date", new Date().toISOString().split('T')[0]); // Current date in YYYY-MM-DD format
            frappe.db.get_doc('User', frappe.session.user)
            .then(doc => {
                console.log(doc)
                localStorage.setItem("session_user", doc.full_name);
            })
        }, 2000);
        report.refresh()
	},

};