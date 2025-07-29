// Copyright (c) 2025, NexTash and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Vehicle Service Request", {
//   refresh: function(frm) {
//     // For Employee (Driver / Staff)
//     frappe.call({
//       method: 'frappe.client.get_list',
//       args: {
//         doctype: 'Employee',
//         fields: ['employee_name'],
//         limit_page_length: 1000
//       },
//       callback: function(r) {
//         if (r.message) {
//           let names = r.message.map(emp => emp.employee_name);
//           frm.set_df_property('driver__staff', 'options', [''].concat(names));
//         }
//       }
//     });

//     // For Vehicle
//     frappe.call({
//       method: 'frappe.client.get_list',
//       args: {
//         doctype: 'Vehicle',
//         fields: ['license_plate'],
//         limit_page_length: 1000
//       },
//       callback: function(r) {
//         if (r.message) {
//           let vehicles = r.message.map(v => v.license_plate);
//           frm.set_df_property('vehicle', 'options', [''].concat(vehicles));
//         }
//       }
//     });
//   },

//   vehicle: function(frm) {
//     if (frm.doc.vehicle) {
//       frappe.call({
//         method: 'frappe.client.get',
//         args: {
//           doctype: 'Vehicle',
//           name: frm.doc.vehicle
//         },
//         callback: function(r) {
//           if (r.message) {
//             frm.set_value('model', r.message.model || '');
//             frm.set_value('make', r.message.make || '');
//           }
//         }
//       });
//     } else {
//       frm.set_value('model', '');
//       frm.set_value('make', '');
//     }
//   }
// });
