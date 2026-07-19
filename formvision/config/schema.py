from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Rect":
        return cls(
            x=int(data["x"]),
            y=int(data["y"]),
            width=int(data["width"]),
            height=int(data["height"]),
        )


@dataclass(frozen=True)
class FieldConfig:
    id: str
    label: str
    type: str
    roi: Rect
    validators: tuple[str, ...] = ()
    options: tuple[str, ...] = ()
    demo_value: Any = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FieldConfig":
        return cls(
            id=str(data["id"]),
            label=str(data.get("label", data["id"])),
            type=str(data["type"]),
            roi=Rect.from_dict(data["roi"]),
            validators=tuple(data.get("validators", [])),
            options=tuple(data.get("options", [])),
            demo_value=data.get("demo_value"),
        )


@dataclass(frozen=True)
class FormTemplate:
    template_id: str
    page_width: int
    page_height: int
    fields: tuple[FieldConfig, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormTemplate":
        page_size = data["page_size"]
        return cls(
            template_id=str(data["template_id"]),
            page_width=int(page_size["width"]),
            page_height=int(page_size["height"]),
            fields=tuple(FieldConfig.from_dict(field) for field in data["fields"]),
        )
