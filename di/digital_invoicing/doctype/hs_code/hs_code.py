import frappe
from frappe.model.document import Document


class HSCode(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.Text | None
		hs_code: DF.Data
		uom: DF.Link | None
	# end: auto-generated types

	pass
