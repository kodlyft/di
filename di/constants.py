DI_BASE_URL = "https://gw.fbr.gov.pk"
DI_POST_PROD = "/di_data/v1/di/postinvoicedata"
DI_POST_SANDBOX = "/di_data/v1/di/postinvoicedata_sb"
DI_VALIDATE_PROD = "/di_data/v1/di/validateinvoicedata"
DI_VALIDATE_SANDBOX = "/di_data/v1/di/validateinvoicedata_sb"

POS_SANDBOX_URL = "https://esp.fbr.gov.pk:8244/FBR/v1/api/Live/PostData"
POS_PROD_URL = "https://gw.fbr.gov.pk/imsp/v1/api/Live/PostData"
POS_SUCCESS_CODES = {"100", 100}

REF_BASE_V1 = "https://gw.fbr.gov.pk/pdi/v1"
REF_BASE_V2 = "https://gw.fbr.gov.pk/pdi/v2"

STATL_BASE_URL = "https://gw.fbr.gov.pk/dist/v1"

SRO_REQUIRED_SALE_TYPES = [
	"Exempt goods",
	"Goods at zero-rate",
	"3rd Schedule Goods",
	"Goods as per SRO.297(|)/2023",
	"Goods at Reduced Rate",
]

INVOICE_TYPE_SALE = "Sale Invoice"
INVOICE_TYPE_DEBIT_NOTE = "Debit Note"

PAYMENT_MODE_CASH = 1
PAYMENT_MODE_CARD = 2
PAYMENT_MODE_GIFT_VOUCHER = 3
PAYMENT_MODE_LOYALTY = 4
PAYMENT_MODE_MIXED = 5
PAYMENT_MODE_CHEQUE = 6

POS_INVOICE_NEW = 1
POS_INVOICE_CREDIT = 3
POS_INVOICE_3RD_SCHEDULE_NEW = 11
POS_INVOICE_3RD_SCHEDULE_CREDIT = 12
