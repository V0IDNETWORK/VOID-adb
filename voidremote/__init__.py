"""
VoidRemote - Wireless Android Remote Controller over ADB
========================================================

A cross-platform desktop application for controlling Android devices
wirelessly through ADB (Android Debug Bridge).

Author: V0IDNETWORK <ilianothingg@gmail.com>
Website: http://voidNetwork.ir/
GitHub: https://github.com/V0IDNETWORK/VoidRemote
License: MIT
"""

__version__ = "1.0.0"
__author__ = "V0IDNETWORK"
__email__ = "ilianothingg@gmail.com"
__license__ = "MIT"
__url__ = "https://github.com/V0IDNETWORK/VoidRemote"
__description__ = "Wireless Android Remote Controller over ADB"

from voidremote.utils.logging import setup_logging

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
    "__description__",
    "setup_logging",
]
