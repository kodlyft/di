frappe.ui.form.on("Item", {
	hs_code(frm) {
		if (frm.doc.hs_code) {
			frappe.db.get_value("HS Code", frm.doc.hs_code, "uom").then((r) => {
				if (r && r.message) {
					frm.set_value("hs_uom", r.message.uom);
				}
			});
		} else {
			frm.set_value("hs_uom", "");
		}
	},

	setup(frm) {
		frm.set_query("sale_type", () => {
			let company = frappe.defaults.get_default("company");
			if (company) {
				return {
					query: "di.api.get_sale_types_for_company",
					filters: { company: company },
				};
			}
			return {};
		});
	},
});
