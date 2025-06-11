// Copyright (c) 2025, Ahmed Emam and contributors
// For license information, please see license.txt

// frappe.ui.form.on("WH Massage", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('WH Massage', {
    refresh: function(frm) {
        // Show button only if status is empty (None)
        if (!frm.doc.status) {
            frm.add_custom_button(__('Send WhatsApp Message'), function() {
                frappe.call({
                    method: 'wassenger_integration.api.send_whatsapp_message',
                    args: {
                        docname: frm.doc.name
                    },
                    freeze: true,
                    callback: function(r) {
                        if (!r.exc) {
                            frm.reload_doc();
                        }
                    }
                });
            });
        }
    }
});