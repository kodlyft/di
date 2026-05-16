frappe.ui.form.on("POS Profile", {
	refresh(frm) {
		di_pos_toggle_fields(frm);
	},

	enable_fbr_integration(frm) {
		di_pos_toggle_fields(frm);
	}
});

function di_pos_toggle_fields(frm) {
	let enabled = frm.doc.enable_fbr_integration;
	frm.toggle_display("fbr_environment", enabled);
	frm.toggle_display("fbr_pos_id", enabled);
	frm.toggle_display("fbr_bearer_token", enabled);
	frm.toggle_display("fbr_api_url", enabled);
}
