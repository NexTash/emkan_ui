frappe.query_reports["Division-wise Report Segregation"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "reqd": 1,
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
        // {
        //     "fieldname": "finance_book",
        //     "label": __("Finance Book"),
        //     "fieldtype": "Link",
        //     "options": "Finance Book",
        //     "reqd": 0
        // },
        // {
        //     "fieldname": "fiscal_year",
        //     "label": __("Fiscal Year"),
        //     "fieldtype": "Select",
        //     "options": [
        //         { "value": "Yearly", "label": __("Yearly") },
        //         { "value": "Date Range", "label": __("Date Range") }
        //     ],
        //     "reqd": 1,
        //     "on_change": function(value) {
        //         let startYearField = frappe.query_report.get_filter_value('start_year');
        //         let endYearField = frappe.query_report.get_filter_value('end_year');

        //         if (value === "Yearly") {
        //             // Clear date fields if Yearly is selected
        //             frappe.query_report.set_filter_value('start_year', '');
        //             frappe.query_report.set_filter_value('end_year', '');
        //             frappe.query_report.get_filter('start_year').df.fieldtype = "Link";
        //             frappe.query_report.get_filter('end_year').df.fieldtype = "Link";
        //             frappe.query_report.refresh();
        //         } else {
        //             // Switch to date range fields if Date Range is selected
        //             frappe.query_report.get_filter('start_year').df.fieldtype = "Date";
        //             frappe.query_report.get_filter('end_year').df.fieldtype = "Date";
        //             frappe.query_report.refresh();
        //         }
        //     }
        // },
        // {
        //     "fieldname": "start_year",
        //     "label": __("Start Year"),
        //     "fieldtype": "Link",
        //     "options": "Fiscal Year",
        //     "reqd": 1
        // },
        // {
        //     "fieldname": "end_year",
        //     "label": __("End Year"),
        //     "fieldtype": "Link",
        //     "options": "Fiscal Year",
        //     "reqd": 1
        // },
        // {
        //     "fieldname": "periodicity",
        //     "label": __("Periodicity"),
        //     "fieldtype": "Select",
        //     "options": ["Yearly", "Quarterly", "Monthly"],
        //     "reqd": 1
        // },
        // {
        //     "fieldname": "currency",
        //     "label": __("Currency"),
        //     "fieldtype": "Link",
        //     "options": "Currency",
        //     "reqd": 0
        // },
        {
            "fieldname": "cost_center",
            "label": __("Cost Center/Divisions"),
            "fieldtype": "Link",
            "options": "Cost Center",
            "reqd": 0
        },
        // {
        //     "fieldname": "vehicle",
        //     "label": __("Vehicle"),
        //     "fieldtype": "MultiSelect",
        //     "options": "Vehicle",
        //     "reqd": 0
        // },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "reqd": 0
        },
        // {
        //     "fieldname": "selected_view",
        //     "label": __("Select View"),
        //     "fieldtype": "Select",
        //     "options": [
        //         { "value": "Report", "label": __("Report View") },
        //         { "value": "Growth", "label": __("Growth View") },
        //         { "value": "Margin", "label": __("Margin View") }
        //     ],
        //     "default": "Report",
        //     "reqd": 1
        // },
        // {
        //     "fieldname": "accumulated_values",
        //     "label": __("Accumulated Values"),
        //     "fieldtype": "Check",
        //     "default": 1,
        //     "reqd": 0
        // },
        // {
        //     "fieldname": "include_default_book_entries",
        //     "label": __("Include Default FB Entries"),
        //     "fieldtype": "Check",
        //     "default": 1,
        //     "reqd": 0
        // }
    ]
};