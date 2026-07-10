# VoidRemote

<div align="center">

```
██╗   ██╗ ██████╗ ██╗██████╗ ██████╗ ███████╗███╗   ███╗ ██████╗ ████████╗███████╗
██║   ██║██╔═══██╗██║██╔══██╗██╔══██╗██╔════╝████╗ ████║██╔═══██╗╚══██╔══╝██╔════╝
██║   ██║██║   ██║██║██║  ██║██████╔╝█████╗  ██╔████╔██║██║   ██║   ██║   █████╗
╚██╗ ██╔╝██║   ██║██║██║  ██║██╔══██╗██╔══╝  ██║╚██╔╝██║██║   ██║   ██║   ██╔══╝
 ╚████╔╝ ╚██████╔╝██║██████╔╝██║  ██║███████╗██║ ╚═╝ ██║╚██████╔╝   ██║   ███████╗
  ╚═══╝   ╚═════╝ ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚══════╝
```

**Wireless Android Remote Controller over ADB**

[![CI](https://github.com/V0IDNETWORK/VoidRemote/actions/workflows/ci.yml/badge.svg)](https://github.com/V0IDNETWORK/VoidRemote/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#features) · [Installation](#installation) · [Quick Start](#quick-start) · [CLI Reference](#cli-reference) · [GUI Guide](#gui-guide) · [Architecture](#architecture) · [Contributing](#contributing)

</div>

---

## Overview

VoidRemote is a cross-platform desktop application for **wirelessly controlling Android devices** through ADB (Android Debug Bridge). It pairs with Android's built-in Wireless Debugging feature — no root required, no third-party server software, no cables.

Built entirely in Python with a modern PySide6 GUI and an enterprise-grade CLI, VoidRemote is designed for developers, testers, power users, and anyone who needs reliable, scriptable remote control of Android devices.

---

## Features

### 🔗 Device Management
- Discover USB and wireless ADB devices automatically
- Pair devices via Android 11+ Wireless Debugging (no USB needed after first pair)
- Auto-reconnect trusted devices on startup
- Full device info: model, Android version, CPU ABI, resolution, battery, IP, RAM, storage

### 🖥️ Screen Mirroring
- Low-latency screen streaming using `screenrecord` + `screencap`
- Resizable mirror window, fullscreen support
- Screenshot capture (CLI + GUI)
- Screen recording with configurable bitrate and resolution

### 🖱️ Input Control
- Mouse click, double-click, long press
- Swipe and drag gestures
- Keyboard text input with Unicode support
- Hardware key events (Home, Back, Volume, Power, etc.)
- Clipboard paste

### 📁 File Manager
- Browse device file system
- Upload local files to device
- Download device files
- Subdirectory navigation with history

### 📦 APK Management
- Install APK (with replace/downgrade options)
- Uninstall packages by name
- Batch install via CLI

### 🖥 Shell Terminal
- Embedded ADB shell with command history
- Up/down arrow navigation through history
- Colored output (errors in red)
- Per-device terminal sessions

### 📊 Real-time Monitoring
- CPU usage with sparkline graph
- RAM usage (used / total)
- Battery level and temperature
- Live metric cards with circular gauges

### 🤖 Automation
- Record macro sequences (tap, swipe, text, keyevent)
- Play back macros with speed control and repeat
- Save/load macro library as JSON
- CLI integration for scripting

### 🔧 Enterprise CLI
- 25+ commands with colored output
- JSON output mode (`--json`) for scripting
- Verbose and debug flags
- `voidremote doctor` for setup diagnosis

### 🎨 Modern GUI
- Dark theme with professional typography
- Sidebar navigation with 7 panels
- Device cards with live battery/state indicators
- Real-time log viewer with level filtering
- Settings panel with live save

---

## Screenshots

> _GUI screenshots will be added after first public release._

| Dashboard | Shell | Monitor |
|-----------|-------|---------|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Shell](docs/screenshots/shell.png) | ![Monitor](docs/screenshots/monitor.png) |

---

## Requirements

| Requirement | Minimum Version |
|-------------|-----------------|
| Python | 3.12+ |
| ADB (Platform Tools) | 1.0.41+ |
| Android | 11+ (for Wireless Debugging) |
| OS | Windows 10+, macOS 12+, Ubuntu 22.04+ |

### Python Dependencies
- **PySide6** — Qt6 GUI framework
- **click** — CLI framework
- **rich** — Terminal formatting
- **pydantic** — Settings validation
- **psutil** — System metrics
- **Pillow** — Image processing
- **cryptography** — Secure config storage

---

## Installation

### From PyPI (recommended)

```bash
pip install voidremote
```

### From Source

```bash
git clone https://github.com/V0IDNETWORK/VoidRemote.git
cd VoidRemote
pip install -e ".[dev]"
```

### Verify Installation

```bash
voidremote doctor
```

---

## Quick Start

### 1. Enable Wireless Debugging on Android

1. Go to **Settings → About Phone** and tap **Build Number** 7 times to enable Developer Options
2. Go to **Settings → Developer Options → Wireless Debugging**
3. Enable **Wireless Debugging**

### 2. Pair Your Device

```bash
# Interactive pairing wizard
voidremote pair

# Or provide all arguments at once
voidremote pair 192.168.1.50 37001 123456
```

In the Wireless Debugging screen, tap **"Pair device with pairing code"** and enter the IP, port, and 6-digit code shown.

### 3. Connect

```bash
voidremote connect 192.168.1.50
```

### 4. List Devices

```bash
voidremote devices
```

### 5. Launch GUI

```bash
voidremote-gui
```

---

## CLI Reference

```
voidremote [OPTIONS] COMMAND

Options:
  -v, --verbose     Enable verbose output
  --debug           Enable debug logging
  --json            Output as JSON
  -V, --version     Show version and exit
  -h, --help        Show help

Commands:
  devices       List connected ADB devices
  pair          Pair via Wireless Debugging
  connect       Connect to device over TCP/IP
  disconnect    Disconnect a wireless device
  info          Show detailed device information
  screenshot    Capture a screenshot
  shell         Execute ADB shell command
  tap           Tap at screen coordinates
  swipe         Swipe between two points
  text          Type text on device
  keyevent      Send hardware key event
  install       Install an APK
  uninstall     Uninstall an app package
  push          Push file to device
  pull          Pull file from device
  reboot        Reboot device
  battery       Show battery status
  wifi          Show WiFi information
  doctor        Diagnose setup issues
  version       Show version information
  logs          View application logs
  config        Manage configuration
```

### Examples

```bash
# Take a screenshot
voidremote screenshot 192.168.1.50:5555 ~/Desktop/screen.png

# Type text
voidremote text 192.168.1.50:5555 "hello world"

# Tap center of a 1080x2400 screen
voidremote tap 192.168.1.50:5555 540 1200

# Swipe up (scroll down)
voidremote swipe 192.168.1.50:5555 540 1500 540 500 --duration 400

# Press back
voidremote keyevent 192.168.1.50:5555 4

# Install APK
voidremote install 192.168.1.50:5555 ~/Downloads/app.apk

# Run shell command
voidremote shell 192.168.1.50:5555 getprop ro.build.version.release

# JSON output for scripting
voidremote --json devices | jq '.[].serial'

# Battery info as JSON
voidremote --json battery 192.168.1.50:5555

# Debug mode
voidremote --debug connect 192.168.1.50
```

---

## GUI Guide

Launch the GUI with:

```bash
voidremote-gui
```

### Sidebar Navigation

| Panel | Description |
|-------|-------------|
| 📱 Devices | Dashboard with device cards |
| 🖥️ Mirror | Screen mirroring launcher |
| 🖥 Shell | ADB shell terminal |
| 📊 Monitor | Real-time performance graphs |
| 📁 Files | File manager |
| ⚙️ Settings | Application settings |
| 📋 Logs | Live log viewer |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F5` | Refresh device list |
| `Ctrl+Shift+C` | Open Connect dialog |
| `Ctrl+Shift+P` | Open Pair dialog |
| `Ctrl+Q` | Quit |

---

## Architecture

```
voidremote/
├── adb/                 # ADB subprocess layer
│   ├── client.py        # AdbClient — raw command execution
│   └── device_parser.py # Parse ADB output into typed models
├── cli/
│   └── main.py          # Click CLI — all 25+ commands
├── config/
│   └── settings.py      # Pydantic settings with JSON persistence
├── controllers/
│   └── app_controller.py # DI root — unified facade for CLI + GUI
├── core/
│   └── automation.py    # Macro recording and playback engine
├── models/
│   └── device.py        # Pydantic device models
├── network/
│   └── discovery.py     # Subnet scanner for ADB device discovery
├── services/
│   ├── device_service.py   # Device lifecycle + trusted device store
│   ├── input_service.py    # Touch/keyboard/key event control
│   └── monitor_service.py  # Background polling thread for metrics
├── ui/
│   ├── app.py           # QApplication bootstrap
│   ├── main_window.py   # Main window + sidebar navigation
│   ├── theme.py         # Dark QSS theme + color palette
│   ├── dialogs/         # Modal dialogs (pair, connect)
│   ├── views/           # Full-panel views (dashboard, shell, etc.)
│   └── widgets/         # Reusable widgets (DeviceCard, LogView, etc.)
└── utils/
    ├── logging.py       # Rotating file + colored console logging
    └── security.py      # Input validation + injection prevention
```

### Design Principles

- **Single ADB client**: One `AdbClient` instance shared via `AppController` (dependency injection root)
- **Layered architecture**: `CLI/GUI → Controller → Services → ADB Client`
- **Type safety**: Pydantic models for all data, type hints everywhere, mypy-compatible
- **Security-first**: All user input validated before reaching ADB; no shell=True anywhere
- **Thread safety**: Background tasks run in `QThread` (GUI) or `threading.Thread` (services)

---

## Configuration

VoidRemote stores its configuration in your platform's standard config directory:

| OS | Path |
|----|------|
| Windows | `%APPDATA%\V0IDNETWORK\VoidRemote\settings.json` |
| macOS | `~/Library/Application Support/VoidRemote/settings.json` |
| Linux | `~/.config/VoidRemote/settings.json` |

```bash
# Show current config
voidremote config --show

# Reset to defaults
voidremote config --reset
```

Configuration can also be set via environment variables:

```bash
VOIDREMOTE_ADB__PATH=/usr/local/bin/adb
VOIDREMOTE_UI__THEME=dark
VOIDREMOTE_LOG__LEVEL=DEBUG
```

---

## Troubleshooting

### ADB not found

```bash
# Verify ADB is installed
adb version

# If not, install Android Platform Tools:
# https://developer.android.com/tools/releases/platform-tools
# Then set the path in settings:
voidremote config --show
```

### Device not connecting wirelessly

1. Ensure device and PC are on the **same WiFi network**
2. Check that **Wireless Debugging** is enabled in Developer Options
3. Try re-pairing: `voidremote pair`
4. Verify firewall is not blocking port 5555

### Unauthorized device

```bash
# Revoke and re-authorize ADB
adb kill-server
voidremote connect 192.168.1.50
# Accept the "Allow USB debugging" prompt on the device
```

### GUI won't start

```bash
# Check PySide6 is installed
python -c "import PySide6; print(PySide6.__version__)"

# On Linux, install Qt system dependencies:
sudo apt install libgl1 libglib2.0-0 libdbus-1-3
```

---

## FAQ

**Q: Do I need root access?**  
A: No. VoidRemote uses Android's standard ADB interface which requires only Developer Options to be enabled.

**Q: Does it work over mobile data / VPN?**  
A: ADB TCP/IP works over any IP network where port 5555 is reachable. VPN tunnels are supported if they carry TCP traffic.

**Q: Can I control multiple devices at once?**  
A: Yes. The CLI accepts `--serial` arguments and the GUI maintains separate sessions per device.

**Q: Is my device data sent anywhere?**  
A: No. VoidRemote communicates only with your device via ADB. No telemetry, no cloud, no tracking.

**Q: Which Android versions are supported?**  
A: ADB input and shell commands work on Android 4.0+. Wireless Debugging pairing requires Android 11+.

---

## Contributing

Contributions are warmly welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

```bash
# Fork the repo and clone your fork
git clone https://github.com/YOUR_USERNAME/VoidRemote.git
cd VoidRemote

# Install dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v

# Check formatting
black --check voidremote/ tests/
ruff check voidremote/ tests/
```

---

## Roadmap

- [ ] **v1.1**: Live screen mirroring via `scrcpy` Python bindings
- [ ] **v1.2**: Multi-device simultaneous control
- [ ] **v1.3**: Macro scheduling (cron-style task runner)
- [ ] **v1.4**: Plugin system for custom device profiles
- [ ] **v2.0**: Android TV remote support

---

## License

MIT License — see [LICENSE](LICENSE) for full text.

---

## Author

**V0IDNETWORK**

> V0IDNETWORK is an ongoing, open research effort to document — rigorously and accurately — how the modern Internet's circumvention and surveillance technologies actually work at the protocol level, in support of a more open and resilient Internet.

| Platform | Link |
|----------|------|
| 🌐 Website | [voidNetwork.ir](http://voidNetwork.ir/) |
| 💻 GitHub | [@V0IDNETWORK](https://github.com/V0IDNETWORK) |
| 💼 LinkedIn | [ilianothing](https://www.linkedin.com/in/ilianothing) |
| 📸 Instagram | [@ilianothing](https://www.instagram.com/ilianothing) |
| ▶️ YouTube | [@locailife](https://youtube.com/@locailife?si=KMPEWpxZg2CpgfX_) |
| 🎯 TryHackMe | [ilianothingg](https://tryhackme.com/p/ilianothingg) |
| ✍️ Medium | [@ilianothingg](https://medium.com/@ilianothingg) |
| 📬 Telegram | [@voidxMaster](https://t.me/voidxMaster) |
| 📧 Email | [ilianothingg@gmail.com](mailto:ilianothingg@gmail.com) |

---

<div align="center">

Made with ❤️ by V0IDNETWORK · [Star this repo](https://github.com/V0IDNETWORK/VoidRemote) if you find it useful!

</div>
