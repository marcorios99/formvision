from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Extraction:
    value: Any
    confidence: float
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)
