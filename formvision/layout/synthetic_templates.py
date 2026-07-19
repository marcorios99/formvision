import json
from pathlib import Path

import cv2
import numpy as np

from formvision.config.schema import FormTemplate
from formvision.layout.mnist_digits import MnistDigitRenderer


class SyntheticFormFactory:
    """Generates synthetic forms for demos and tests."""

    def create_sample(
        self,
        template: FormTemplate,
        output_path: str | Path,
        document_id: str = "FORM-2026-0001",
        selected_answers: dict[str, str] | None = None,
    ) -> Path:
        selected_answers = selected_answers or {"question_01": "C", "question_02": "A"}
        canvas = np.full(
            (template.page_height, template.page_width, 3), 255, dtype=np.uint8
        )
        self._draw_header(canvas, document_id, template.template_id)

        for field in template.fields:
            if field.type == "omr":
                self._draw_omr_field(canvas, field, selected_answers.get(field.id))
            elif field.type in {"ocr", "icr"}:
                self._draw_text_field(canvas, field, document_id)

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(path), canvas)
        return path

    def _draw_header(self, canvas: np.ndarray, document_id: str, template_id: str) -> None:
        cv2.putText(
            canvas,
            "Synthetic Form Reader",
            (80, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.4,
            (20, 20, 20),
            3,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            f"Document: {document_id}",
            (80, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (40, 40, 40),
            2,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            f"Template: {template_id}",
            (80, 185),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (80, 80, 80),
            2,
            cv2.LINE_AA,
        )
        self._draw_qr(canvas, f"{document_id}|{template_id}", (950, 55), 180)

    def _draw_qr(self, canvas: np.ndarray, value: str, origin: tuple[int, int], size: int) -> None:
        try:
            import qrcode
        except ImportError:
            cv2.rectangle(canvas, origin, (origin[0] + size, origin[1] + size), (0, 0, 0), 2)
            cv2.putText(
                canvas,
                "QR optional",
                (origin[0] + 18, origin[1] + 95),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (30, 30, 30),
                1,
                cv2.LINE_AA,
            )
            return

        qr = qrcode.QRCode(border=1, box_size=8)
        qr.add_data(value)
        qr.make(fit=True)
        qr_image = np.array(qr.make_image(fill_color="black", back_color="white").convert("RGB"))
        qr_image = cv2.resize(qr_image, (size, size), interpolation=cv2.INTER_NEAREST)
        x, y = origin
        canvas[y : y + size, x : x + size] = qr_image

    def _draw_text_field(self, canvas: np.ndarray, field, document_id: str) -> None:
        x, y, w, h = field.roi.x, field.roi.y, field.roi.width, field.roi.height
        cv2.rectangle(canvas, (x, y), (x + w, y + h), (20, 20, 20), 2)
        value = "12345678" if field.type == "icr" else "ANA TORRES"
        cv2.putText(
            canvas,
            field.label,
            (x, y - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (70, 70, 70),
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            value if field.id != "document_id" else document_id,
            (x + 18, y + round(h * 0.65)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (15, 15, 15),
            2,
            cv2.LINE_AA,
        )

    def _draw_omr_field(self, canvas: np.ndarray, field, selected: str | None) -> None:
        x, y, w, h = field.roi.x, field.roi.y, field.roi.width, field.roi.height
        cv2.putText(
            canvas,
            field.label,
            (x, y - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (70, 70, 70),
            1,
            cv2.LINE_AA,
        )
        spacing = w // max(1, len(field.options))
        radius = min(18, h // 4)
        for index, option in enumerate(field.options):
            cx = x + spacing * index + spacing // 2
            cy = y + h // 2
            cv2.circle(canvas, (cx, cy), radius, (20, 20, 20), 2)
            cv2.putText(
                canvas,
                option,
                (cx - 8, cy + radius + 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (45, 45, 45),
                2,
                cv2.LINE_AA,
            )
            if selected == option:
                cv2.circle(canvas, (cx, cy), radius - 5, (30, 30, 30), -1)


class SyntheticOmrSheetFactory:
    """Creates an original OMR sheet and its matching JSON layout."""

    bubble_outline_color = (190, 80, 190)

    def create_sheet(
        self,
        image_path: str | Path,
        layout_path: str | Path,
        document_id: str = "OMR-DEMO-0001",
        questions: int = 20,
        options: tuple[str, ...] = ("A", "B", "C", "D"),
        handwriting_source: str = "opencv",
        mnist_root: str | Path = "data/external/mnist",
        student_code: str = "12345678",
        full_name: str = "ANA TORRES",
        exam_date: str = "2026-06-12",
        signature: str = "",
        fill_answers: bool = True,
        seed: int | None = None,
    ) -> tuple[Path, Path]:
        rng = np.random.default_rng(seed)
        student_code = self._resolve_student_code(student_code, rng)
        width, height = 1240, 1754
        canvas = np.full((height, width, 3), 255, dtype=np.uint8)
        fields: list[dict] = []

        self._draw_alignment_markers(canvas)
        self._draw_title(canvas)
        self._draw_qr(canvas, f"{document_id}|synthetic_omr_v1", (965, 70), 170)
        fields.extend(
            self._draw_identity_block(
                canvas,
                handwriting_source,
                mnist_root,
                student_code,
                full_name,
                exam_date,
                signature,
                seed,
            )
        )
        fields.extend(self._draw_question_grid(canvas, questions, options, fill_answers))
        self._draw_footer(canvas)

        layout = {
            "template_id": "synthetic_omr_v1",
            "page_size": {"width": width, "height": height},
            "fields": fields,
        }

        image_output = Path(image_path)
        layout_output = Path(layout_path)
        image_output.parent.mkdir(parents=True, exist_ok=True)
        layout_output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(image_output), canvas)
        with layout_output.open("w", encoding="utf-8") as file:
            json.dump(layout, file, indent=2)
        return image_output, layout_output

    def _resolve_student_code(self, student_code: str, rng: np.random.Generator) -> str:
        if student_code.lower() != "random":
            return student_code
        return "".join(str(int(digit)) for digit in rng.integers(0, 10, size=8))

    def _draw_qr(self, canvas: np.ndarray, value: str, origin: tuple[int, int], size: int) -> None:
        SyntheticFormFactory()._draw_qr(canvas, value, origin, size)

    def _draw_alignment_markers(self, canvas: np.ndarray) -> None:
        marker_size = 42
        margin = 42
        height, width = canvas.shape[:2]
        for x, y in (
            (margin, margin),
            (width - margin - marker_size, margin),
            (margin, height - margin - marker_size),
            (width - margin - marker_size, height - margin - marker_size),
        ):
            cv2.rectangle(canvas, (x, y), (x + marker_size, y + marker_size), (0, 0, 0), -1)

    def _draw_title(self, canvas: np.ndarray) -> None:
        cv2.putText(
            canvas,
            "Synthetic OMR Answer Sheet",
            (95, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.25,
            (20, 20, 20),
            3,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            "Generated demo form - no real student or exam data",
            (98, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (85, 85, 85),
            1,
            cv2.LINE_AA,
        )
        cv2.putText(
            canvas,
            "Exam code is encoded in the QR symbol",
            (98, 205),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.66,
            (70, 70, 70),
            1,
            cv2.LINE_AA,
        )

    def _draw_identity_block(
        self,
        canvas: np.ndarray,
        handwriting_source: str,
        mnist_root: str | Path,
        student_code: str,
        full_name: str,
        exam_date: str,
        signature: str,
        seed: int | None,
    ) -> list[dict]:
        fields = []
        specs = [
            ("student_code", "Student Code", "icr", 95, 270, 335, 72, ["required", "digits:8"]),
            ("full_name", "Full Name", "ocr", 470, 270, 560, 72, ["required"]),
            ("exam_date", "Date", "ocr", 95, 390, 260, 68, ["required"]),
            ("signature", "Signature", "ocr", 395, 390, 635, 68, []),
        ]
        values = {
            "student_code": student_code,
            "full_name": full_name,
            "exam_date": exam_date,
            "signature": signature,
        }
        for field_id, label, field_type, x, y, width, height, validators in specs:
            cv2.putText(
                canvas,
                label,
                (x, y - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (70, 70, 70),
                1,
                cv2.LINE_AA,
            )
            cv2.rectangle(canvas, (x, y), (x + width, y + height), (25, 25, 25), 2)
            if field_id == "student_code":
                self._draw_handwritten_digits(
                    canvas,
                    values[field_id],
                    x + 18,
                    y + 52,
                    source=handwriting_source,
                    mnist_root=mnist_root,
                    seed=seed,
                )
            elif values[field_id]:
                cv2.putText(
                    canvas,
                    values[field_id],
                    (x + 16, y + 46),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.75,
                    (25, 25, 25),
                    2,
                    cv2.LINE_AA,
                )
            fields.append(
                {
                    "id": field_id,
                    "label": label,
                    "type": field_type,
                    "roi": {"x": x, "y": y, "width": width, "height": height},
                    "validators": validators,
                    "demo_value": values[field_id],
                }
            )
        return fields

    def _draw_handwritten_digits(
        self,
        canvas: np.ndarray,
        value: str,
        x: int,
        baseline_y: int,
        source: str = "opencv",
        mnist_root: str | Path = "data/external/mnist",
        seed: int | None = None,
    ) -> None:
        if source == "mnist":
            try:
                digit_image = MnistDigitRenderer(mnist_root, seed=seed).render(value, height=46)
                y = baseline_y - digit_image.shape[0] + 6
                canvas[y : y + digit_image.shape[0], x : x + digit_image.shape[1]] = digit_image
                return
            except (FileNotFoundError, ImportError, RuntimeError):
                pass

        for index, digit in enumerate(value):
            offset_x = x + index * 34
            offset_y = baseline_y + (-2 if index % 2 == 0 else 3)
            scale = 1.0 if index % 3 else 1.08
            thickness = 2 if index % 2 else 3
            cv2.putText(
                canvas,
                digit,
                (offset_x, offset_y),
                cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                scale,
                (18, 18, 18),
                thickness,
                cv2.LINE_AA,
            )

    def _draw_question_grid(
        self,
        canvas: np.ndarray,
        questions: int,
        options: tuple[str, ...],
        fill_answers: bool = True,
    ) -> list[dict]:
        fields = []
        start_x, start_y = 105, 560
        column_gap = 535
        row_gap = 82
        option_gap = 72
        bubble_radius = 16
        questions_per_column = int(np.ceil(questions / 2))

        for question_number in range(1, questions + 1):
            column = 0 if question_number <= questions_per_column else 1
            row = question_number - 1 if column == 0 else question_number - questions_per_column - 1
            x = start_x + column * column_gap
            y = start_y + row * row_gap
            selected = options[(question_number + 1) % len(options)] if fill_answers else None

            cv2.putText(
                canvas,
                f"{question_number:02d}",
                (x, y + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                (45, 45, 45),
                2,
                cv2.LINE_AA,
            )
            for option_index, option in enumerate(options):
                cx = x + 78 + option_index * option_gap
                cy = y + 25
                cv2.circle(canvas, (cx, cy), bubble_radius, self.bubble_outline_color, 2)
                cv2.putText(
                    canvas,
                    option,
                    (cx - 9, cy + 42),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (75, 75, 75),
                    1,
                    cv2.LINE_AA,
                )
                if selected == option:
                    cv2.circle(canvas, (cx, cy), bubble_radius - 5, (35, 35, 35), -1)

            fields.append(
                {
                    "id": f"question_{question_number:02d}",
                    "label": f"Question {question_number}",
                    "type": "omr",
                    "roi": {
                        "x": x + 52,
                        "y": y,
                        "width": option_gap * (len(options) - 1) + 52,
                        "height": 54,
                    },
                    "options": list(options),
                    "validators": ["required", "single_choice"],
                }
            )
        return fields

    def _draw_footer(self, canvas: np.ndarray) -> None:
        cv2.line(canvas, (95, 1655), (1145, 1655), (190, 190, 190), 1)
        cv2.putText(
            canvas,
            "Portfolio demo sheet. Layout coordinates are generated as JSON.",
            (95, 1690),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (95, 95, 95),
            1,
            cv2.LINE_AA,
        )
