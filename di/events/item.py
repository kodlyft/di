"""Item event handlers for Digital Invoicing."""
import frappe


def before_save(doc, method=None):
	"""Hook: before_save on Item. Auto-populate HS UOM from HS Code."""
	if doc.get("hs_code") and not doc.get("hs_uom"):
		uom = frappe.db.get_value("HS Code", doc.hs_code, "uom")
		if uom:
			doc.hs_uom = uom
