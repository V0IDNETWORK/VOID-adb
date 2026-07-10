# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x.x   | ✅ Active support |
| < 1.0   | ❌ No support |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in VoidRemote, please report it responsibly:

### Preferred: GitHub Private Security Advisory

Use GitHub's [Private Security Advisory](https://github.com/V0IDNETWORK/VoidRemote/security/advisories/new) feature to report vulnerabilities confidentially.

### Alternative: Email

Send details to **ilianothingg@gmail.com** with:
- Subject line: `[SECURITY] VoidRemote - <brief description>`
- A clear description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Any suggested mitigations (if known)

### What to Expect

- **Acknowledgement**: Within 48 hours
- **Initial assessment**: Within 5 business days
- **Fix timeline**: Depends on severity
  - Critical (RCE, data exfiltration): 7 days
  - High: 14 days
  - Medium: 30 days
  - Low: Next planned release

### Disclosure Policy

- We follow **Coordinated Vulnerability Disclosure (CVD)**
- We will credit you in the release notes (unless you prefer to remain anonymous)
- We ask that you keep the vulnerability confidential until a fix is released

---

## Security Design

VoidRemote is designed with the following security principles:

### Input Validation
- All user-supplied values (IP addresses, ports, paths, package names) are validated before use
- Pairing codes must match the 6-digit format exactly
- Device paths must be absolute and free of traversal sequences

### Command Injection Prevention
- ADB commands are passed as argument lists (never shell strings)
- Shell arguments containing metacharacters (`;`, `|`, `` ` ``, `$`, `<`, `>`, `\`) are rejected
- `subprocess.run()` is called without `shell=True` anywhere in the codebase

### File Operations
- Local file paths are resolved to absolute paths before use
- Device file paths are validated to prevent `../` traversal
- File transfers go through the validated `push`/`pull` ADB commands only

### Configuration
- Settings are stored in the platform's standard user config directory
- No credentials or secrets are stored in plaintext
- ADB pairing codes are used once and not persisted

### Network
- VoidRemote communicates only with devices on the local network via ADB
- No outbound connections to external servers (except for optional update checks)
- Subnet scanning is opt-in and local-only

### Dependencies
- Dependencies are pinned to minimum versions with known security posture
- Dependabot is configured for automated dependency updates
- No abandoned or unmaintained dependencies

---

## Known Limitations

- VoidRemote inherits ADB's security model: any device authorized for ADB debugging has broad system access. Use on trusted networks only.
- Screen mirroring content is transmitted unencrypted over the local ADB TCP connection.
- Macro files are stored as plain JSON and are not integrity-checked before execution.
