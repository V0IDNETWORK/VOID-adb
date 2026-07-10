# Contributing to VoidRemote

Thank you for your interest in contributing! VoidRemote welcomes contributions of all kinds — bug reports, feature requests, documentation improvements, and code changes.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

---

## Code of Conduct

This project follows a simple principle: **be respectful and constructive**. Harassment, discrimination, or personal attacks will not be tolerated.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/VoidRemote.git
   cd VoidRemote
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/V0IDNETWORK/VoidRemote.git
   ```

---

## Development Setup

### Prerequisites

- Python 3.12+
- ADB (Android Platform Tools)
- Git

### Install Dependencies

```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install in editable mode with all dev dependencies
pip install -e ".[dev]"
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

This runs Black, Ruff, and basic checks automatically on every commit.

### Verify Setup

```bash
voidremote doctor
pytest tests/ -v --no-header
```

---

## Project Structure

```
voidremote/
├── adb/            # ADB subprocess layer — keep security-sensitive
├── cli/            # Click CLI commands
├── config/         # Pydantic settings
├── controllers/    # DI root (AppController)
├── core/           # Domain logic (automation, etc.)
├── models/         # Typed data models
├── network/        # Network utilities
├── services/       # Business logic services
├── ui/             # PySide6 GUI
└── utils/          # Shared utilities
```

**Layer rules** (strict, no circular imports):
```
CLI/GUI → Controller → Services → ADB Client
                    ↘ Models ↙
```

---

## Code Standards

### Formatting

```bash
# Format all code
black voidremote/ tests/

# Lint
ruff check voidremote/ tests/

# Type check
mypy voidremote/
```

### Style Guidelines

- **Type hints everywhere** — all public functions must have full type annotations
- **Docstrings** — all public modules, classes, and functions must have docstrings
- **Line length** — 100 characters max (Black enforces this)
- **No `shell=True`** — use list-form subprocess calls only; validate all inputs first
- **No bare `except`** — always catch specific exception types
- **Logging over print** — use `logging.getLogger(__name__)`, never `print()` in library code
- **Pathlib over os.path** — use `pathlib.Path` for all file operations

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(cli): add --timeout flag to connect command
fix(adb): handle timeout in shell command
docs(readme): update wireless setup instructions
test(security): add tests for path traversal prevention
refactor(ui): extract DeviceCard into separate module
chore(deps): bump PySide6 to 6.7.1
```

---

## Testing

### Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only (fast, no ADB required)
pytest tests/unit/ -v

# CLI tests
pytest tests/cli/ -v

# With coverage report
pytest tests/ --cov=voidremote --cov-report=html
```

### Writing Tests

- **Unit tests** go in `tests/unit/` — mock all external dependencies
- **Integration tests** go in `tests/integration/` — use mocked ADB client
- **CLI tests** go in `tests/cli/` — use `click.testing.CliRunner`
- Every new feature **must** include tests
- Bug fixes **should** include a regression test

### Test Fixtures

Shared fixtures are in `tests/conftest.py`. Prefer using existing fixtures before creating new ones.

```python
def test_my_feature(sample_device: Device, mock_adb: MagicMock) -> None:
    ...
```

---

## Submitting Changes

1. **Create a branch** from `develop` (not `main`):
   ```bash
   git checkout -b feat/my-feature develop
   ```

2. **Make your changes**, following the code standards above

3. **Write or update tests**

4. **Run the full test suite**:
   ```bash
   pytest tests/ -v
   black --check voidremote/ tests/
   ruff check voidremote/ tests/
   ```

5. **Update `CHANGELOG.md`** under `[Unreleased]`

6. **Push and open a Pull Request** against `develop`

7. Fill in the pull request template completely

8. Wait for CI to pass and a maintainer review

---

## Adding a New CLI Command

1. Add the command function in `voidremote/cli/main.py`:
   ```python
   @cli.command("mycommand")
   @click.argument("serial")
   @click.pass_obj
   def cmd_mycommand(obj: CliContext, serial: str) -> None:
       """Short description."""
       obj.init_controller()
       ...
   ```

2. Add the corresponding method to `AppController` if needed

3. Write a test in `tests/cli/test_cli.py`

4. Update the CLI Reference section in `README.md`

---

## Adding a New GUI View

1. Create `voidremote/ui/views/my_view.py` inheriting from `QWidget`
2. Add to `voidremote/ui/views/__init__.py`
3. Import and add to the stack in `voidremote/ui/main_window.py`
4. Add a sidebar item in `NAV_ITEMS`

---

## Release Process

Releases are managed by maintainers only:

1. Update `CHANGELOG.md` — move `[Unreleased]` to `[X.Y.Z] - YYYY-MM-DD`
2. Bump version in `pyproject.toml` and `voidremote/__init__.py`
3. Commit: `chore(release): bump version to X.Y.Z`
4. Tag: `git tag -a vX.Y.Z -m "Release X.Y.Z"`
5. Push tag: `git push origin vX.Y.Z`
6. GitHub Actions handles the rest (wheel build → PyPI publish → GitHub Release)

---

## Questions?

Open a [GitHub Discussion](https://github.com/V0IDNETWORK/VoidRemote/discussions) or reach out via [Telegram](https://t.me/voidxMaster).
