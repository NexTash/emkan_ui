frappe.query_reports["Division-wise Report"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1,
            "default": frappe.defaults.get_default("Company")
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
            "fieldname": "cost_center",
            "label": __("Cost Center/Divisions"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "reqd": 0
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "reqd": 0
        },
        ]
};