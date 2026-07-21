from datetime import datetime, timezone
from pathlib import Path

from formvision.config.schema import FormTemplate
from formvision.extractors.barcode_extractor import BarcodeExtractor
from formvision.extractors.icr.base import IcrEngine
from formvision.extractors.ocr.base import OcrEngine
from formvision.extractors.omr_extractor import OmrExtractor
from formvision.image_processing.color_dropout import MagentaDropout
from formvision.image_processing.loader import ImageLoader
from formvision.image_processing.page_frame_normalizer import PageFrameNormalizer
from formvision.image_processing.perspective import PerspectiveCorrector
from formvision.layout.coordinate_mapper import CoordinateMapper
from formvision.pipeline.result_models import BarcodeResult, FieldResult, FormProcessingResult
from formvision.validators.field_validator import FieldValidator


class FormProcessingPipeline:
    """Coordinates loading, QR reading, field extraction and validation."""

    def __init__(
        self,
        loader: ImageLoader | None = None,
        perspective: PerspectiveCorrector | None = None,
        mapper: CoordinateMapper | None = None,
        barcode_extractor: BarcodeExtractor | None = None,
        frame_normalizer: PageFrameNormalizer | None = None,
        magenta_dropout: MagentaDropout | None = None,
        omr_extractor: OmrExtractor | None = None,
        ocr_extractor: OcrEngine | None = None,
        icr_extractor: IcrEngine | None = None,
        validator: FieldValidator | None = None,
    ) -> None:
        self.loader = loader or ImageLoader()
        self.perspective = perspective or PerspectiveCorrector()
        self.mapper = mapper or CoordinateMapper()
        self.barcode_extractor = barcode_extractor or BarcodeExtractor()
        self.frame_normalizer = frame_normalizer or PageFrameNormalizer()
        self.magenta_dropout = magenta_dropout or MagentaDropout()
        self.omr_extractor = omr_extractor or OmrExtractor()
        self.ocr_extractor = ocr_extractor
        self.icr_extractor = icr_extractor
        self.validator = validator or FieldValidator()

    def process(
        self,
        image_path: str | Path,
        template: FormTemplate,
        template_image_path: str | Path | None = None,
        align: bool = False,
    ) -> FormProcessingResult:
        image = self.loader.load(image_path)
        aligned = self._align_image(image, template, template_image_path, align)
        cleaned = self.magenta_dropout.apply(aligned)
        barcode = self.barcode_extractor.extract(aligned)
        document_id, detected_template_id = self._parse_barcode(barcode.value)

        fields: dict[str, FieldResult] = {}
        has_issues = False
        for field in sorted(template.fields, key=self._field_order):
            source_image = cleaned
            roi = self.mapper.crop_field(
                source_image, field, template.page_width, template.page_height
            )
            extraction = self._extract_field(field, roi)
            issues = self.validator.validate(field, extraction.value)
            has_issues = has_issues or bool(issues)
            fields[field.id] = FieldResult(
                value=extraction.value,
                confidence=round(extraction.confidence, 4),
                source=extraction.source,
                valid=not issues,
                issues=[issue.__dict__ for issue in issues],
                metadata=extraction.metadata,
            )

        status = "processed_with_warnings" if has_issues else "processed"
        return FormProcessingResult(
            document_id=document_id or Path(image_path).stem,
            template_id=detected_template_id or template.template_id,
            status=status,
            barcode=BarcodeResult(
                value=barcode.value,
                type="QR_CODE" if barcode.value else "NONE",
                confidence=barcode.confidence,
                source=barcode.source,
            ),
            fields=fields,
            metadata={
                "image_path": str(image_path),
                "template_image_path": str(template_image_path) if template_image_path else None,
                "aligned": align,
                "magenta_dropout": True,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def _align_image(
        self,
        image,
        template: FormTemplate,
        template_image_path: str | Path | None,
        align: bool,
    ):
        if not align:
            return self.perspective.correct(image)
        if template_image_path:
            reference = self.loader.load(template_image_path)
            return self.frame_normalizer.normalize_to_reference(image, reference).image
        target_width = template.page_width
        target_height = template.page_height
        return self.frame_normalizer.normalize(
            image,
            target_width=target_width,
            target_height=target_height,
        ).image

    def _field_order(self, field) -> tuple[int, str]:
        order = {"omr": 0, "icr": 1, "ocr": 2}
        return (order.get(field.type, 99), field.id)

    def _extract_field(self, field, roi):
        if field.type == "omr":
            return self.omr_extractor.extract(roi, field)
        if field.type == "icr":
            if self.icr_extractor is None:
                raise RuntimeError(
                    f"ICR engine is required for field '{field.id}'. "
                    "Configure FormProcessingPipeline(icr_extractor=...)."
                )
            return self.icr_extractor.extract(roi, field.demo_value)
        if field.type == "ocr":
            if self.ocr_extractor is None:
                raise RuntimeError(
                    f"OCR engine is required for field '{field.id}'. "
                    "Configure FormProcessingPipeline(ocr_extractor=...)."
                )
            return self.ocr_extractor.extract(roi, field.demo_value)
        raise ValueError(f"Unsupported field type: {field.type}")

    def _parse_barcode(self, value: str | None) -> tuple[str | None, str | None]:
        if not value:
            return None, None
        parts = value.split("|", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return value, None
