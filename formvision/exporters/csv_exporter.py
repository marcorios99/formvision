import csv
from pathlib import Path

from formvision.pipeline.result_models import FormProcessingResult


class CsvExporter:
    def export(self, result: FormProcessingResult, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["document_id", "field_id", "value", "confidence", "valid"])
            for field_id, field in result.fields.items():
                writer.writerow(
                    [
                        result.document_id,
                        field_id,
                        field.value,
                        f"{field.confidence:.3f}",
                        field.valid,
                    ]
                )
        return path
