"""
Database module for excursor.

Stores data in a local lancedb
"""

from typing import Final

import lance
import lancedb

uri: Final[str] = "game_catalog"
