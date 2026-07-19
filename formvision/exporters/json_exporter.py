import json
from dataclasses import asdict
from pathlib import Path

from formvision.pipeline.result_models import FormProcessingResult


class JsonExporter:
    def export(self, result: FormProcessingResult, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(asdict(result), file, indent=2, ensure_ascii=False)
        return path
