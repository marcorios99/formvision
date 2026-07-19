import json
from pathlib import Path

from formvision.config.schema import FormTemplate


class TemplateLoader:
    """Loads a public JSON layout definition."""

    def load(self, layout_path: str | Path) -> FormTemplate:
        path = Path(layout_path)
        with path.open("r", encoding="utf-8") as file:
            return FormTemplate.from_dict(json.load(file))
