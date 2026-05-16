import frappe
from frappe.model.document import Document


class TransactionType(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		transaction_desc: DF.Data
		transaction_type_id: DF.Int
	# end: auto-generated types

	pass
