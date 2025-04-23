// Copyright (c) 2025, NexTash and contributors
// For license information, please see license.txt

frappe.ui.form.on('Employee Letter', {
    employee(frm) {
        populate_salary_components_if_needed(frm);
    },

    letter_type(frm) {
        populate_salary_components_if_needed(frm);
    }
});

function populate_salary_components_if_needed(frm) {
    if (!frm.doc.employee || frm.doc.letter_type !== "Salary Increment") return;

    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Salary Structure Assignment',
            filters: {
                employee: frm.doc.employee
            },
            fields: ['name']
        },
        callback(r) {
            if (r.message && r.message.length > 0) {
                const assignment_name = r.message[0].name;

                frappe.call({
                    method: 'frappe.client.get',
                    args: {
                        doctype: 'Salary Structure Assignment',
                        name: assignment_name
                    },
                    callback: function(res) {
                        const assignment = res.message;

                        frm.clear_table('salary_component');

                        const components = [
                            { label: 'Basic', value: assignment.base },
                            { label: 'Living Allowance', value: assignment.custom_living_allowance },
                            { label: 'Food Allowance', value: assignment.custom_food_allowance },
                            { label: 'Telephone Allowance', value: assignment.custom_telephone_allowance },
                            { label: 'Special Allowance', value: assignment.custom_special_allowance },
                            { label: 'Other Allowance', value: assignment.custom_other_allowance },
                            { label: 'Variable', value: assignment.variable },
                            { label: 'Project Allowance', value: assignment.custom_project_allowance },
                            { label: 'Fuel Allowance', value: assignment.custom_fuel_allowance },
                            { label: 'Performance Allowance', value: assignment.custom_performance_allowance }
                        ];

                        components.forEach(comp => {
                            if (comp.value) {
                                let row = frm.add_child('salary_component');
                                row.component = comp.label;
                                row.current_salary = comp.value;
                            }
                        });

                        frm.refresh_field('salary_component');
                    }
                });
            } else {
                frappe.msgprint(__('No Salary Structure Assignment found for this employee.'));
            }
        }
    });
}

