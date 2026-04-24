"""
Database module for excursor.

Stores data in a local lancedb
"""

from typing import Final

import lance
import lancedb

from excursor.database import CharacterSchema

uri: Final[str] = "game_catalog"

def create_character_table():
    schema = CharacterSchema.schema()
    
    