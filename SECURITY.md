# Security Policy

Security matters here because this app handles tax payloads, invoice metadata,
and credentials used to communicate with FBR services.

## Supported Versions

| Version / Branch | Supported |
| --- | --- |
| `develop` | Yes |
| Latest tagged release | Yes |
| Older releases | No |

## Reporting a Vulnerability

Do not open public GitHub issues for vulnerabilities.

Report security issues through one of these channels:

1. Email `security@kodlyft.com`
2. If GitHub private vulnerability reporting is enabled for the repository, use
   the repository security advisory flow

Use the subject line: `[SECURITY] di - short summary`

Please include:

- A clear description of the issue
- The affected component, endpoint, or workflow
- Reproduction steps or a proof of concept
- Expected impact
- Suggested remediation if you have one
- Whether the issue affects sandbox, production, or both

## Response Targets

- Acknowledgement within 2 business days
- Initial triage within 5 business days
- Ongoing status updates for valid reports until resolution or mitigation

## In Scope

- Authentication or authorization bypasses
- Exposure of FBR bearer tokens or other secrets
- Injection flaws, including SQL, command, or unsafe template execution
- Cross-site scripting or unsafe client-side rendering
- Privilege escalation through DocType permissions or whitelisted methods
- Leakage of taxpayer, invoice, or customer data
- Integrity issues that allow incorrect invoice submission or manipulation

## Out of Scope

- Vulnerabilities in upstream Frappe or ERPNext that are not caused by this app
- Support requests or configuration mistakes without a security impact
- Missing best practices without a demonstrable exploit path
- Denial-of-service reports without a working reproduction path

## Deployment Guidance

- Use HTTPS for all external API traffic
- Store credentials only in encrypted Frappe password fields or equivalent secret
  storage
- Restrict access to DI Settings, DI logs, and posting actions by role
- Rotate FBR credentials regularly
- Review application logs for unusual posting, validation, or sync activity
- Keep Frappe, ERPNext, and this repository updated

## Responsible Disclosure

Please give maintainers reasonable time to investigate and ship a fix before
public disclosure. Avoid accessing, changing, or exfiltrating data beyond what
is needed to demonstrate the issue safely.
