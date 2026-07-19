import sqlite3
from pathlib import Path

from formvision.pipeline.result_models import FormProcessingResult


class SqliteExporter:
    """Optional local persistence for demos; no external database required."""

    def export(self, result: FormProcessingResult, db_path: str | Path) -> Path:
        path = Path(db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS form_results (
                    document_id TEXT,
                    template_id TEXT,
                    field_id TEXT,
                    value TEXT,
                    confidence REAL,
                    valid INTEGER
                )
                """
            )
            for field_id, field in result.fields.items():
                connection.execute(
                    """
                    INSERT INTO form_results
                    (document_id, template_id, field_id, value, confidence, valid)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        result.document_id,
                        result.template_id,
                        field_id,
                        str(field.value) if field.value is not None else None,
                        field.confidence,
                        int(field.valid),
                    ),
                )
        return path
