"""Company event handlers for Digital Invoicing."""
import frappe
from frappe import _


def before_save(doc, method=None):
	"""Hook: before_save on Company. Validate no duplicate sale types."""
	sale_types = doc.get("di_sale_types") or []
	seen = set()
	for row in sale_types:
		st = row.get("sale_type")
		if st in seen:
			frappe.throw(_("Duplicate sale type: {0}").format(st))
		seen.add(st)
