# VoidRemote Architecture

## Overview

VoidRemote follows a layered architecture that cleanly separates concerns and enables both the CLI and GUI to share the same business logic without duplication.

```
┌──────────────────────────────────────────────────────────────┐
│                       Entry Points                            │
│         CLI (click)              GUI (PySide6 QApplication)  │
└────────────────────┬─────────────────────┬───────────────────┘
                     │                     │
                     ▼                     ▼
┌──────────────────────────────────────────────────────────────┐
│                   AppController                               │
│           Dependency injection root — single instance        │
│     Owns AdbClient, DeviceService, InputService, Monitor     │
└──────────┬───────────────────────────────────────────────────┘
           │
           ├─────────────────────────────────────────┐
           ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────────┐
│    DeviceService     │              │      InputService         │
│  Device discovery,   │              │  tap, swipe, text,        │
│  pairing, connect,   │              │  keyevent, scroll         │
│  trusted devices     │              └──────────────────────────┘
└──────────┬───────────┘
           │                          ┌──────────────────────────┐
           │                          │    MonitorService         │
           │                          │  Background polling:      │
           │                          │  CPU, RAM, battery temp   │
           │                          └──────────────────────────┘
           ▼
┌──────────────────────────────────────────────────────────────┐
│                       AdbClient                               │
│          subprocess wrapper around the `adb` binary          │
│     _run_sync() / _run_async() — timeout, error handling     │
└──────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Entry Points (`cli/`, `ui/`)
- Parse user input (CLI arguments / GUI events)
- Call `AppController` methods
- Format and display output
- Never call `AdbClient` directly

### AppController (`controllers/app_controller.py`)
- Owns all service instances (single source of truth)
- Provides a clean, unified facade API
- Handles initialization and shutdown lifecycle
- Injected with `AppSettings` for configuration

### Services (`services/`)
- `DeviceService`: device lifecycle (discover → pair → connect → disconnect → remember)
- `InputService`: all touch and key input operations
- `MonitorService`: background thread polling device metrics

### ADB Layer (`adb/`)
- `AdbClient`: raw subprocess execution of ADB commands
- `device_parser.py`: parses raw ADB output into typed models
- No business logic — pure data transformation and I/O

### Models (`models/`)
- Pydantic models for all domain objects
- Validated at construction time
- Shared by all layers — no duplication

### Config (`config/`)
- `AppSettings`: pydantic-settings with JSON persistence
- Loaded once at startup via `get_settings()` singleton
- Environment variable override support

### Utils (`utils/`)
- `security.py`: input validation and sanitization (called before any ADB command)
- `logging.py`: rotating file + colored console logging setup

## Threading Model

```
Main Thread (Qt Event Loop)
    │
    ├── QThread: RefreshWorker      (device list refresh)
    ├── QThread: ShellWorker        (ADB shell command)
    ├── QThread: PairWorker         (ADB pair)
    ├── QThread: ConnectWorker      (ADB connect)
    ├── QThread: ListDirWorker      (file listing)
    └── QThread: TransferWorker     (push/pull)

Daemon Threads (MonitorService)
    └── threading.Thread per device (metric polling loop)
```

All background workers emit Qt signals to deliver results back to the main thread safely.

## Security Boundaries

```
User Input
    │
    ▼
utils/security.py       ← validate_host(), validate_port(), sanitize_shell_arg()
    │
    ▼
AdbClient._run_sync()   ← list-form args only, no shell=True
    │
    ▼
subprocess.run()        ← OS-level ADB binary
```

## File Organization

```
voidremote/
├── __init__.py           version, package metadata
├── adb/
│   ├── __init__.py
│   ├── client.py         AdbClient, AdbError, AdbCommandResult
│   └── device_parser.py  parse_devices_output, parse_battery, …
├── cli/
│   ├── __init__.py
│   └── main.py           Click CLI group + all commands
├── config/
│   ├── __init__.py
│   └── settings.py       AppSettings, AdbSettings, UISettings, …
├── controllers/
│   ├── __init__.py
│   └── app_controller.py AppController
├── core/
│   ├── __init__.py
│   └── automation.py     MacroRecorder, MacroPlayer, MacroLibrary
├── models/
│   ├── __init__.py
│   └── device.py         Device, DeviceInfo, BatteryInfo, …
├── network/
│   ├── __init__.py
│   └── discovery.py      scan_subnet, scan_host
├── services/
│   ├── __init__.py
│   ├── device_service.py  DeviceService
│   ├── input_service.py   InputService, KeyCode
│   └── monitor_service.py MonitorService, DeviceSnapshot
├── ui/
│   ├── __init__.py
│   ├── app.py            QApplication bootstrap + main()
│   ├── main_window.py    MainWindow (sidebar + stack)
│   ├── theme.py          Colors, DARK_STYLESHEET, apply_dark_theme()
│   ├── dialogs/
│   │   ├── connect_dialog.py
│   │   └── pair_dialog.py
│   ├── views/
│   │   ├── dashboard_view.py
│   │   ├── files_view.py
│   │   ├── monitor_view.py
│   │   ├── settings_view.py
│   │   └── shell_view.py
│   └── widgets/
│       ├── device_card.py
│       ├── log_view.py
│       └── metric_gauge.py
└── utils/
    ├── __init__.py
    ├── logging.py
    └── security.py
```

## Dependency Graph (no cycles)

```
models ──────────────────────────────────────────────────────► (no deps)
config ──────────────────────────────────────────────────────► models
utils  ──────────────────────────────────────────────────────► (no deps)
adb    ──────────────────────────────────────────────────────► models, utils
services ────────────────────────────────────────────────────► adb, models, config
core   ──────────────────────────────────────────────────────► models
controllers ─────────────────────────────────────────────────► services, adb, models, config
cli    ──────────────────────────────────────────────────────► controllers, models, utils
ui     ──────────────────────────────────────────────────────► controllers, models, config
```
