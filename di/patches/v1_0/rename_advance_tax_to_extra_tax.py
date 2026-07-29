import frappe


def execute():
	"""Rename the `Advance Tax` DI tax type to `Extra Tax`.

	FBR DI maps this tax to the `extraTax` field, so the option was renamed to
	match. Existing rows still hold the old value and would otherwise become
	invalid select values and stop being picked up by the payload builder.
	"""
	if not frappe.db.has_column("Sales Taxes and Charges", "di_tax_type"):
		return

	table = frappe.qb.DocType("Sales Taxes and Charges")
	(
		frappe.qb.update(table)
		.set(table.di_tax_type, "Extra Tax")
		.where(table.di_tax_type == "Advance Tax")
	).run()
