"""
Security utilities for VoidRemote.

Input validation, command injection prevention, and safe operations.
"""

from __future__ import annotations

import ipaddress
import re
import shlex
from pathlib import Path
from typing import Optional


# Characters that must not appear in ADB shell arguments
_SHELL_INJECTION_PATTERN = re.compile(r"[;&|`$<>\\]")
_SAFE_PACKAGE_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9._]{1,255}$")
_SAFE_FILENAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-. ()]+$')
_PORT_RE = re.compile(r"^\d{1,5}$")


def validate_ip_address(address: str) -> str:
    """
    Validate that a string is a valid IPv4 or IPv6 address.

    Args:
        address: IP address string to validate.

    Returns:
        The validated address string.

    Raises:
        ValueError: If the address is not valid.
    """
    try:
        parsed = ipaddress.ip_address(address)
        return str(parsed)
    except ValueError as exc:
        raise ValueError(f"Invalid IP address: {address!r}") from exc


def validate_host(host: str) -> str:
    """
    Validate a host (IP or hostname) for use in ADB connections.

    Args:
        host: Hostname or IP address.

    Returns:
        Stripped, validated host string.

    Raises:
        ValueError: If host is empty or contains invalid characters.
    """
    host = host.strip()
    if not host:
        raise ValueError("Host cannot be empty")
    if len(host) > 253:
        raise ValueError("Hostname too long")
    # Try IP address first
    try:
        return validate_ip_address(host)
    except ValueError:
        pass
    # Validate hostname (RFC 1123)
    hostname_re = re.compile(
        r"^(?:[a-zA-Z0-9]"
        r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*)?$"
    )
    if not hostname_re.match(host):
        raise ValueError(f"Invalid hostname: {host!r}")
    return host


def validate_port(port: int | str) -> int:
    """
    Validate a network port number.

    Args:
        port: Port as integer or string.

    Returns:
        Validated port as integer.

    Raises:
        ValueError: If port is out of range.
    """
    try:
        p = int(port)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Port must be an integer, got: {port!r}") from exc
    if not (1 <= p <= 65535):
        raise ValueError(f"Port must be 1-65535, got: {p}")
    return p


def validate_pairing_code(code: str) -> str:
    """
    Validate an ADB wireless pairing code.

    Pairing codes are typically 6 digits.

    Args:
        code: Pairing code string.

    Returns:
        Validated code (stripped).

    Raises:
        ValueError: If code format is invalid.
    """
    code = code.strip()
    if not code:
        raise ValueError("Pairing code cannot be empty")
    if not re.match(r"^\d{6}$", code):
        raise ValueError("Pairing code must be exactly 6 digits")
    return code


def sanitize_shell_arg(arg: str) -> str:
    """
    Sanitize a single argument intended for ADB shell execution.

    Raises ValueError if the argument contains injection characters.

    Args:
        arg: Shell argument to sanitize.

    Returns:
        Shell-quoted safe string.

    Raises:
        ValueError: If arg contains shell metacharacters.
    """
    if _SHELL_INJECTION_PATTERN.search(arg):
        raise ValueError(
            f"Shell argument contains forbidden characters: {arg!r}"
        )
    return shlex.quote(arg)


def sanitize_shell_args(args: list[str]) -> list[str]:
    """Sanitize a list of shell arguments."""
    return [sanitize_shell_arg(a) for a in args]


def validate_package_name(package: str) -> str:
    """
    Validate an Android package name.

    Args:
        package: Android package name (e.g. com.example.app).

    Returns:
        Validated package name.

    Raises:
        ValueError: If package name is invalid.
    """
    package = package.strip()
    if not _SAFE_PACKAGE_PATTERN.match(package):
        raise ValueError(f"Invalid Android package name: {package!r}")
    return package


def validate_device_path(path: str) -> str:
    """
    Validate a path on the Android device.

    Ensures it's an absolute path without null bytes or parent traversal tricks.

    Args:
        path: Absolute device path.

    Returns:
        Validated path string.

    Raises:
        ValueError: If path is unsafe.
    """
    if not path.startswith("/"):
        raise ValueError(f"Device path must be absolute, got: {path!r}")
    if "\x00" in path:
        raise ValueError("Device path contains null byte")
    # Normalize to remove // or trailing /
    p = Path(path)
    normalized = str(p)
    if ".." in normalized.split("/"):
        raise ValueError(f"Device path contains parent traversal: {path!r}")
    return normalized


def validate_local_path(path: Path) -> Path:
    """
    Validate a local file system path.

    Args:
        path: Local path to validate.

    Returns:
        Resolved path.

    Raises:
        ValueError: If path is unsafe or doesn't exist for reading.
    """
    resolved = path.resolve()
    if "\x00" in str(resolved):
        raise ValueError("Path contains null byte")
    return resolved


def is_safe_filename(name: str) -> bool:
    """Return True if name is safe for use as a file/directory name."""
    return bool(_SAFE_FILENAME_PATTERN.match(name)) and ".." not in name
