# Digital Invoicing (DI)

FBR Digital Invoicing and POS Fiscal integration for ERPNext.

This app integrates Pakistan's Federal Board of Revenue (FBR) Digital Invoicing
System (PRAL DI API v1.12) and POS Fiscal services with ERPNext so teams can
submit, validate, and track tax-compliant invoices inside their ERP workflow. You can find the documentation [here](https://docs.kodlyft.com/digital-invoicing/introduction)

## Highlights

- Post and validate invoices with FBR's Digital Invoicing API
- Fiscalize POS invoices through the FBR POS Integration Services API
- Handle return invoices as debit notes automatically
- Generate FBR-compliant QR codes for posted invoices
- Sync FBR reference data such as provinces, HS codes, UOMs, and schedules
- Verify buyer and seller status using the FBR STATL service
- Support both sales and purchase invoice submission flows
- Test against bundled sandbox scenarios before production rollout

## Requirements

| Dependency       | Version    |
| ---------------- | ---------- |
| Python           | >= 3.10    |
| Frappe Framework | >= 15.60.0 |
| ERPNext          | >= 15.60.0 |
| qrcode           | >= 8.2     |

## Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/kodlyft/di --branch develop
bench setup requirements
bench --site your-site.com install-app di
bench --site your-site.com migrate
```

## Configuration

### 1. DI Settings

Create a **DI Settings** record for each company that needs Digital Invoicing:

- Set **Company**
- Enable **Digital Invoicing**
- Choose **Sandbox** or **Production**
- Add the FBR **Access Token**
- Fill **NTN/CNIC**, **Province**, and **Address**

### 2. Customer Setup

For each customer that should be reported through DI:

- Enable **Digital Invoicing**
- Fill **NTN/CNIC**
- Select **Province**
- Set **Registration Type**
- Fill **DI Address**

### 3. Item Setup

Under the DI settings section on each Item:

- Set **HS Code**
- Set **Sale Type**
- Fill any applicable **SRO** fields

### 4. Tax Setup

On **Sales Taxes and Charges** templates, set the **Tax Type** field to one of:

- `Sales Tax`
- `Further Tax`
- `Extra Tax`

### 5. POS Fiscal Setup

On **POS Profile**:

- Enable **FBR Integration**
- Set **FBR Environment**
- Set **FBR POS ID**
- Set **FBR Bearer Token**

On **Mode of Payment**, set the **FBR Payment Mode Code** from `1` to `6`.

## Usage

### Automatic Posting

When **Auto Post on Submit** is enabled in DI Settings, supported invoices are
posted to FBR automatically during submission.

### Manual Actions

On submitted Sales Invoices, the **Digital Invoicing** menu supports:

- **Post to FBR**
- **Validate with FBR**
- **DI Preview**
- **Verify Buyer**

### Reference Data Sync

Use the **Sync Reference Data** actions in DI Settings to fetch:

- Provinces
- HS Codes
- UOMs
- Sale Types
- SRO Item Codes

## Bundled Fixtures

| Data              | Count |
| ----------------- | ----- |
| Provinces         | 7     |
| HS UOMs           | 31    |
| Sale Types        | 26    |
| Sandbox Scenarios | 28    |

## Development

```bash
cd apps/di
pre-commit install
pre-commit run --all-files
bench --site your-site.com run-tests --app di
```

The repository uses `ruff`, `eslint`, `prettier`, GitHub Actions CI, dependency
review, and CodeQL scanning.

## Project Docs

- [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow and local setup
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations
- [SECURITY.md](SECURITY.md) for vulnerability reporting
- [SUPPORT.md](SUPPORT.md) for usage and support channels
- [CHANGELOG.md](CHANGELOG.md) for release tracking

## Releases

GitHub releases are built from version tags that match `v*`. Release notes are
generated automatically from the tagged changes.

## License

[MIT](LICENSE)
