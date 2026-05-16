import frappe
from frappe.model.document import Document


class Province(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		province_code: DF.Int
		province_name: DF.Data
	# end: auto-generated types

	pass
