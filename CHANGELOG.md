# Changelog

All notable changes to VoidRemote are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
VoidRemote uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Live screen mirroring via scrcpy Python bindings
- Multi-device simultaneous input broadcasting
- Macro task scheduler with cron-style triggers
- Plugin API for custom device profiles
- Android TV remote support

---

## [1.0.0] - 2024-01-15

### Added
- **Core ADB layer** (`voidremote/adb/`) — subprocess-based ADB client with async support
- **Device models** (`voidremote/models/`) — fully typed Pydantic models for Device, BatteryInfo, StorageInfo, CpuInfo, NetworkInfo
- **Configuration system** (`voidremote/config/`) — pydantic-settings with JSON persistence and environment variable overrides
- **Device service** — device discovery, wireless pairing, connection, trusted device persistence
- **Input service** — tap, double-tap, long press, swipe, drag, scroll, text input, hardware key events
- **Monitor service** — background polling for CPU, RAM, battery, temperature metrics
- **Automation engine** — macro recording and playback with MacroLibrary persistence
- **Network discovery** — subnet scanner for ADB device discovery
- **Enterprise CLI** — 25+ Click commands with colored output, JSON mode, verbose/debug flags
- **Modern GUI** — PySide6 dark-theme application with sidebar navigation
  - Dashboard with responsive device card grid
  - Shell view with command history and colored output
  - Monitor view with circular gauges and sparkline graphs
  - File manager with navigation, upload, and download
  - Settings panel with live save
  - Live log viewer with level filtering
  - Pair dialog and Connect dialog
- **Dark theme** — comprehensive QSS stylesheet with design system color palette
- **Security utilities** — input validation, shell injection prevention
- **Structured logging** — rotating file logs + colored console output
- **Comprehensive test suite** — unit, integration, and CLI tests
- **GitHub Actions CI** — lint, type-check, and test on Python 3.12/3.13 × Windows/macOS/Linux
- **GitHub Actions release** — automated wheel build and PyPI publish on tag push
- **Issue templates** — bug report and feature request YAML forms
- **Pull request template**
- **Dependabot configuration**

### Security
- All user inputs validated before reaching ADB subprocess
- No `shell=True` used anywhere in subprocess calls
- Shell argument sanitization prevents command injection
- Device paths validated to prevent traversal attacks
- Package names validated against Android naming rules

---

## [0.1.0] - 2024-01-01

### Added
- Initial project scaffolding
- Basic ADB client prototype
- Proof-of-concept CLI

[Unreleased]: https://github.com/V0IDNETWORK/VoidRemote/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/V0IDNETWORK/VoidRemote/releases/tag/v1.0.0
[0.1.0]: https://github.com/V0IDNETWORK/VoidRemote/releases/tag/v0.1.0
