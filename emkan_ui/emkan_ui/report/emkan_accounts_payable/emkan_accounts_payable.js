// Copyright (c) 2024, NexTash and contributors
// For license information, please see license.txt


frappe.query_reports["Emkan Accounts Payable"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "report_date",
			label: __("Posting Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			on_change: function(report) {
				let report_date = frappe.query_report.get_filter_value('report_date');
				if (report_date) {
					localStorage.setItem("report_date", JSON.stringify({report_date}));
				} else {
					localStorage.setItem("report_date", JSON.stringify({}));
				}
				report.refresh();
			}
		},
		{
			fieldname: "finance_book",
			label: __("Finance Book"),
			fieldtype: "Link",
			options: "Finance Book",
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
					},
				};
			},
		},
		{
			fieldname: "party_account",
			label: __("Payable Account"),
			fieldtype: "Link",
			options: "Account",
			get_query: () => {
				var company = frappe.query_report.get_filter_value("company");
				return {
					filters: {
						company: company,
						account_type: "Payable",
						is_group: 0,
					},
				};
			},
		},
		{
			fieldname: "ageing_based_on",
			label: __("Ageing Based On"),
			fieldtype: "Select",
			options: "Posting Date\nDue Date\nSupplier Invoice Date",
			default: "Due Date",
		},
		{
			fieldname: "range",
			label: __("Ageing Range"),
			fieldtype: "Data",
			default: "30, 60, 90, 120",
		},
		{
			fieldname: "payment_terms_template",
			label: __("Payment Terms Template"),
			fieldtype: "Link",
			options: "Payment Terms Template",
		},
		{
			fieldname: "party_type",
			label: __("Party Type"),
			fieldtype: "Autocomplete",
			options: get_party_type_options(),
			on_change: function () {
				frappe.query_report.set_filter_value("party", "");
				frappe.query_report.toggle_filter_display(
					"supplier_group",
					frappe.query_report.get_filter_value("party_type") !== "Supplier"
				);
			},
		},
		{
			fieldname: "party",
			label: __("Party"),
			fieldtype: "MultiSelectList",
			get_data: function (txt) {
				if (!frappe.query_report.filters) return;

				let party_type = frappe.query_report.get_filter_value("party_type");
				if (!party_type) return;

				return frappe.db.get_link_options(party_type, txt);
			},
			on_change: function () {
				disable_group()

			},
		},
		{
			fieldname: "supplier_group",
			label: __("Supplier Group"),
			fieldtype: "Link",
			options: "Supplier Group",
			hidden: 1,
		},
		{
			fieldname: "group_by_party",
			label: __("Group By Supplier"),
			fieldtype: "Check",
		},
		{
			fieldname: "based_on_payment_terms",
			label: __("Based On Payment Terms"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_remarks",
			label: __("Show Remarks"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_future_payments",
			label: __("Show Future Payments"),
			fieldtype: "Check",
		},
		{
			fieldname: "for_revaluation_journals",
			label: __("Revaluation Journals"),
			fieldtype: "Check",
		},
		{
			fieldname: "ignore_accounts",
			label: __("Group by Voucher"),
			fieldtype: "Check",
		},
		{
			fieldname: "in_party_currency",
			label: __("In Party Currency"),
			fieldtype: "Check",
		},
		{
			fieldname: "handle_employee_advances",
			label: __("Handle Employee Advances"),
			fieldtype: "Check",
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (data && data.bold) {
			value = value.bold();
		}
		return value;
	},

	onload: function (report) {
		report.page.add_inner_button(__("Emkan Payable Summary"), function () {
			var filters = report.get_values();
			frappe.set_route("query-report", "Emkan Payable Summary", { company: filters.company });
		});
		disable_group()
		
	},
};

erpnext.utils.add_dimensions("Emkan Accounts Payable", 9);

function get_party_type_options() {
	let options = [];
	frappe.db
		.get_list("Party Type", { filters: { account_type: "Payable" }, fields: ["name"] })
		.then((res) => {
			res.forEach((party_type) => {
				options.push(party_type.name);
			});
		});
	return options;
}


function disable_group() {
    let party_value = frappe.query_report.get_filter_value("party");

    // Store the party value in localStorage
    if (party_value && party_value.length > 0) {
        localStorage.setItem('party_value', party_value);

        // Disable checkbox and uncheck it
        $('input[data-fieldname="group_by_party"]').prop('checked', false).prop('disabled', true);
        localStorage.setItem('group_by_party', 'disabled');
    } else {
        // Enable checkbox
        $('input[data-fieldname="group_by_party"]').prop('disabled', false);

        // Remove the stored party value from localStorage if not present
        localStorage.removeItem('party_value');
        localStorage.setItem('group_by_party', 'enabled');
    }

    report.refresh();
}