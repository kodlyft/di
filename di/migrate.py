from di.custom_fields import setup_custom_fields


def after_migrate():
	setup_custom_fields()
