"""
Network device discovery utilities.

Scans the local subnet for Android devices with ADB enabled
using TCP port scanning on common ADB ports.
"""

from __future__ import annotations

import ipaddress
import logging
import socket
import threading
from typing import Callable, Optional

logger = logging.getLogger(__name__)

ADB_PORTS = [5555, 5556, 5557, 5558, 5559]
DEFAULT_TIMEOUT = 0.5


def _check_port(host: str, port: int, timeout: float = DEFAULT_TIMEOUT) -> bool:
    """Return True if TCP port is open on host."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, ConnectionRefusedError, TimeoutError):
        return False


def scan_host(host: str, ports: list[int] = ADB_PORTS) -> list[tuple[str, int]]:
    """
    Scan a single host for open ADB ports.

    Returns:
        List of (host, port) tuples where ADB appears to be listening.
    """
    results: list[tuple[str, int]] = []
    for port in ports:
        if _check_port(host, port):
            results.append((host, port))
    return results


def scan_subnet(
    subnet: str,
    ports: list[int] = ADB_PORTS,
    timeout: float = DEFAULT_TIMEOUT,
    max_workers: int = 64,
    on_found: Optional[Callable[[str, int], None]] = None,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> list[tuple[str, int]]:
    """
    Scan an entire subnet for ADB devices.

    Args:
        subnet: CIDR notation subnet (e.g. "192.168.1.0/24").
        ports: List of ports to check.
        timeout: Per-connection timeout in seconds.
        max_workers: Maximum concurrent scan threads.
        on_found: Optional callback called when a device is discovered.
        on_progress: Optional callback(scanned, total) for progress.

    Returns:
        List of (host, port) tuples with open ADB ports.
    """
    try:
        network = ipaddress.ip_network(subnet, strict=False)
    except ValueError as exc:
        raise ValueError(f"Invalid subnet: {subnet!r}") from exc

    hosts = list(network.hosts())
    total = len(hosts)
    results: list[tuple[str, int]] = []
    scanned = 0
    lock = threading.Lock()
    semaphore = threading.Semaphore(max_workers)

    def scan_one(host: str) -> None:
        nonlocal scanned
        with semaphore:
            found = scan_host(host, ports)
            with lock:
                scanned += 1
                results.extend(found)
                if on_found and found:
                    for h, p in found:
                        on_found(h, p)
                if on_progress:
                    on_progress(scanned, total)

    threads = [threading.Thread(target=scan_one, args=(str(h),), daemon=True) for h in hosts]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    logger.info("Subnet scan %s complete: %d hosts scanned, %d found", subnet, total, len(results))
    return results


def get_local_subnet() -> Optional[str]:
    """
    Attempt to determine the local network subnet.

    Returns:
        CIDR string like "192.168.1.0/24", or None if not determinable.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        parts = local_ip.split(".")
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except Exception:
        return None
