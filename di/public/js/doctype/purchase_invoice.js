frappe.ui.form.on("Purchase Invoice", {
	refresh(frm) {
		di_pi_toggle_section(frm);
		di_pi_add_buttons(frm);
	},

	company(frm) {
		di_pi_toggle_section(frm);
	},
});

function di_pi_toggle_section(frm) {
	if (!frm.doc.company) {
		frm.toggle_display("di_section", false);
		return;
	}

	frappe.xcall("di.digital_invoicing.doctype.di_settings.di_settings.is_enabled", {
		company: frm.doc.company,
	}).then((enabled) => {
		frm.toggle_display("di_section", !!enabled);
	});
}

function di_pi_add_buttons(frm) {
	if (frm.doc.docstatus !== 1) return;

	frm.add_custom_button(__("DI Preview"), () => {
		frappe.xcall("di.api.get_invoice_preview", {
			doctype: frm.doc.doctype,
			name: frm.doc.name,
		}).then((payload) => {
			let d = new frappe.ui.Dialog({
				title: __("Digital Invoice Preview"),
				size: "extra-large",
			});
			d.$body.html(
				`<pre style="max-height:500px;overflow:auto;font-size:12px;">${JSON.stringify(payload, null, 2)}</pre>`
			);
			d.show();
		});
	}, __("Digital Invoicing"));

	if (!frm.doc.is_di_posted) {
		frm.add_custom_button(__("Post to FBR"), () => {
			frappe.confirm(
				__("Are you sure you want to post this invoice to FBR?"),
				() => {
					frappe.xcall("di.api.resync_invoice", {
						doctype: frm.doc.doctype,
						name: frm.doc.name,
					}).then(() => {
						frappe.msgprint(__("Invoice posted to FBR successfully"));
						frm.reload_doc();
					});
				}
			);
		}, __("Digital Invoicing"));
	}
}
