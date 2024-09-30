frappe.ui.form.on('Payroll Entry', {
    refresh:function(frm){
		$('[data-label="Get%20Employees"]').hide()
		frm.add_custom_button('Get Employees', () => {
			let filters = {};
			if (frm.doc.designation) {
				filters['designation'] = frm.doc.designation;
			}
			if (frm.doc.branch) {
				filters['branch'] = frm.doc.branch;
			}
			if (frm.doc.department) {
				filters['department'] = frm.doc.department;
			}
			if (frm.doc.grade) {
				filters['grade'] = frm.doc.grade;
			}
			if (frm.doc.custom_employment_type_) {
				filters['employment_type'] = frm.doc.custom_employment_type_;
			}
			frappe.db.get_list('Employee', {
				fields: ['*'],
				filters: filters
			}).then(records => {
				if(records && records.length >= 1){
					console.log(records);
					frm.doc.employees = []
					for(let row of records){
						frm.add_child('employees', {
							employee: row.name,
							employee_name: row.employee_name,
							department: row.department,
							designation: row.designation,
						});
						
						frm.refresh_field('employees');
						var number_of_employees = frm.doc.employees.length;
        
						frm.set_value('number_of_employees', number_of_employees);					}
				}
			})
		})
	}
})