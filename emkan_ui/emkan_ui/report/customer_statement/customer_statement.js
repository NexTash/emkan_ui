// Copyright (c) 2024, nextash and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Statement"] = {
    "filters": [
        {
            fieldname: "customer",
            label: ("Customer"),
            fieldtype: "Link",
            options: "Customer",
            width: 100,
            reqd: 1,
            on_change: function(report) {
                let customer = frappe.query_report.get_filter_value('customer');
                if (customer) {
                    frappe.db.get_doc('Customer', customer)
                        .then(customer_doc => {
                            localStorage.setItem("customer", JSON.stringify({
                                id: customer_doc.name,
                                name: customer_doc.customer_name,

                            }));
        
                            // Handle customer currency
                            if (customer_doc.default_currency) {
                                localStorage.setItem("customer_currency", JSON.stringify({
                                    currency: customer_doc.default_currency,
                                }));
                            } else {
                                let company = frappe.query_report.get_filter_value('company');
                                if (company) {
                                    frappe.db.get_doc('Company', company)
                                        .then(company_doc => {
                                            localStorage.setItem("customer_currency", JSON.stringify({
                                                currency: company_doc.default_currency,
                                            }));
                                        });
                                }
                            }
        
                            // Handle customer primary address
                            if (customer_doc.customer_primary_address) {
                                frappe.db.get_doc('Address', customer_doc.customer_primary_address)
                                    .then(address_doc => {
                                        // Store customer address in localStorage
                                        let address_parts = [
                                            address_doc.address_line1 || "",
                                            address_doc.address_line2 || "",
                                            address_doc.city || "",
                                            address_doc.country || ""
                                        ];
                                        let full_address = address_parts.filter(Boolean).join('<br>');
                                        localStorage.setItem("customer_address", JSON.stringify({
                                            address: full_address
                                        }));
                                    });
                            } else {
                                localStorage.setItem("customer_address", JSON.stringify({
                                    address: ''
                                }));
                            }
        
                            // Handle customer primary contact
                            if (customer_doc.customer_primary_contact) {
                                frappe.db.get_doc('Contact', customer_doc.customer_primary_contact)
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
                                            localStorage.setItem("customer_contact", JSON.stringify({
                                                phone: phone_no,
                                                email: email_id
                                            }));
                                        }, 2000);
                                    });
                            } else {
                                localStorage.setItem("customer_contact", JSON.stringify({
                                    phone: "",
                                    email: ""
                                }));
                            }
                        });
                } else {
                    // Clear customer data from localStorage if no customer is selected
                    localStorage.setItem("customer", JSON.stringify({}));
                    localStorage.setItem("customer_currency", JSON.stringify({}));
                    localStorage.setItem("customer_address", JSON.stringify({}));
                    localStorage.setItem("customer_contact", JSON.stringify({}));
                }
                report.refresh();
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