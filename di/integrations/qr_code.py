"""QR Code generation for FBR Digital Invoicing.

Generates QR Code Version 2 (25x25 modules) as required by FBR.
Returns base64 data URIs for embedding in print formats.
"""

import base64
import io

import frappe


def generate_qr_code(invoice_number):
	"""Generate a QR code for the given FBR invoice number.

	Returns a base64 data URI string suitable for use in <img> tags.
	"""
	if not invoice_number:
		return ""

	try:
		import qrcode
		from qrcode.constants import ERROR_CORRECT_L
	except ImportError:
		frappe.log_error("qrcode library not installed. Run: pip install qrcode[pil]", "QR Code Error")
		return ""

	qr = qrcode.QRCode(
		version=2,
		error_correction=ERROR_CORRECT_L,
		box_size=4,
		border=2,
	)
	qr.add_data(str(invoice_number))
	qr.make(fit=False)

	img = qr.make_image(fill_color="black", back_color="white")

	buffer = io.BytesIO()
	img.save(buffer, format="PNG")
	buffer.seek(0)
	encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

	return f"data:image/png;base64,{encoded}"


def get_fbr_logo_data_uri():
	"""Return the FBR DI logo as a base64 data URI.

	Looks for the logo file in the app's public directory.
	"""
	import os

	logo_path = os.path.join(
		os.path.dirname(os.path.dirname(__file__)),
		"public",
		"images",
		"fbr_di_logo.png",
	)

	if not os.path.exists(logo_path):
		return ""

	with open(logo_path, "rb") as f:
		encoded = base64.b64encode(f.read()).decode("utf-8")

	return f"data:image/png;base64,{encoded}"
