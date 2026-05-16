import frappe
from frappe.model.document import Document


class SaleType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		requires_sro: DF.Check
		sale_type_name: DF.Data
	# end: auto-generated types

	pass
