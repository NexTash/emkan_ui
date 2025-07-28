// Copyright (c) 2025, NexTash and contributors
// For license information, please see license.txt

frappe.ui.form.on("Vehicle Service Log", {
  refresh: function(frm) {
    // For Employee (Driver / Staff)
    frappe.call({
      method: 'frappe.client.get_list',
      args: {
        doctype: 'Employee',
        fields: ['employee_name'],
        limit_page_length: 1000
      },
      callback: function(r) {
        if (r.message) {
          let names = r.message.map(emp => emp.employee_name);
          frm.set_df_property('driver__staff', 'options', [''].concat(names));
        }
      }
    });

    // For Vehicle
    frappe.call({
      method: 'frappe.client.get_list',
      args: {
        doctype: 'Vehicle',
        fields: ['license_plate'],
        limit_page_length: 1000
      },
      callback: function(r) {
        if (r.message) {
          let vehicles = r.message.map(v => v.license_plate);
          frm.set_df_property('vehicle', 'options', [''].concat(vehicles));
        }
      }
    });

    // const reason_options = [
    //   "OIL FILTER", "FUEL FILTER", "A/C FILTER", "A/C COMPLAINT/GAS FILLING", "ENGINE OIL",
    //   "TYRE PUNCTURE", "NEW TYRE PURCHASE", "PERIODICAL SERVICE", "HOSE ASSEMBLE",
    //   "STICKER BRANDING", "ENGINE MOUNTING", "BREAK PAD", "BATTERY", "STARTER MOTOR",
    //   "COMPRESSOR ASSEY", "ISTIMARA/INSPECTION", "WASHING", "O RING", "FAN BELT", "PEDEL ASSEY"
    // ];

    // // Hide original field
    // frm.fields_dict.reason.$wrapper;

    // // Create multiselect
    // frm.reason = frappe.ui.form.make_control({
    //   parent: frm.fields_dict.reason.$wrapper,
    //   df: {
    //     fieldtype: 'MultiSelect',
    //     label: 'Reason',
    //     fieldname: 'reason',
    //     options: reason_options,
    //   },
    //   render_input: true
    // });

    // frm.reason.make_input();

    // // Sync changes to original field
    // frm.reason.$wrapper.on('change', () => {
    //   const selected = frm.reason.get_value();

    //   // Set the value in original hidden field
    //   frappe.db.set_value("Vehicle Service Log", frm.doc.name, "reason", selected.join(","));

    //   // Save the document immediately
    //   frm.save(); // Optional: use only if you want auto-save
    // }); 
  }
});
