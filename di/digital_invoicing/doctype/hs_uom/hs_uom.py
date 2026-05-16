import frappe
from frappe.model.document import Document


class HSUom(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		uom_id: DF.Int
		uom_name: DF.Data
	# end: auto-generated types

	pass
