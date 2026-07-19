from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FieldResult:
    value: Any
    confidence: float
    source: str
    valid: bool
    issues: list[dict[str, str]]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BarcodeResult:
    value: str | None
    type: str
    confidence: float
    source: str


@dataclass(frozen=True)
class FormProcessingResult:
    document_id: str
    template_id: str
    status: str
    barcode: BarcodeResult
    fields: dict[str, FieldResult]
    metadata: dict[str, Any]
