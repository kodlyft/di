import frappe
from di.custom_fields import setup_custom_fields


def after_install():
	setup_custom_fields()
