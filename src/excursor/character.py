from dataclasses import dataclass
import pyarrow as pa
from pyarrow import Schema
from pydantic import BaseModel


class Attribute(BaseModel):
    name: str
    value: float
    cost: float = 1.0


class Character(BaseModel):
    name: str
    age: int
    bio: str
    # physical attributes
    power: Attribute
    speed: Attribute
    kinesthesia: Attribute
    health: Attribute
    fitness: Attribute
    mass: Attribute
    height: Attribute
    # mental attributes
    memory: Attribute
    analysis: Attribute
    insight: Attribute
    focus: Attribute
    discipline: Attribute
    creativity: Attribute
    # social
    eloquence: Attribute
    charm: Attribute
    presence: Attribute
    empathy: Attribute
    # Personality Spectrum
    # aggression: Attribute
    # greed: Attribute
    # selfishness: Attribute


@dataclass
class CharacterSchema:
    @classmethod
    def schema(cls) -> Schema:
        return pa.schema(
            [
                pa.field("name", pa.string()),
                pa.field("age", pa.uint16()),
                pa.field("bio", pa.string()),
                pa.field("power", pa.float32()),
                pa.field("speed", pa.float32()),
                pa.field("kinesthesia", pa.float32()),
                pa.field("health", pa.float32()),
                pa.field("fitness", pa.float32()),
                pa.field("mass", pa.float32()),
                pa.field("height", pa.float32()),
                pa.field("memory", pa.float32()),
                pa.field("analysis", pa.float32()),
                pa.field("insight", pa.float32()),
                pa.field("focus", pa.float32()),
                pa.field("discpline", pa.float32()),
                pa.field("creativity", pa.float32()),
                pa.field("eloquence", pa.float32()),
                pa.field("charm", pa.float32()),
                pa.field("presence", pa.float32()),
                pa.field("empathy", pa.float32()),
            ]
        )
