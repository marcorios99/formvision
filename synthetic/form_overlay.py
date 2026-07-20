from pathlib import Path

import cv2
import numpy as np


class FormOverlay:
    """Places a prepared image inside a rectangular form region."""

    def paste_image(
        self,
        form_path: str | Path,
        overlay_path: str | Path,
        output_path: str | Path,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> Path:
        form = cv2.imread(str(form_path), cv2.IMREAD_COLOR)
        if form is None:
            raise FileNotFoundError(f"Could not read form image: {form_path}")

        overlay = cv2.imread(str(overlay_path), cv2.IMREAD_COLOR)
        if overlay is None:
            raise FileNotFoundError(f"Could not read overlay image: {overlay_path}")

        prepared = self._fit_inside(overlay, width - 24, height - 18)
        target = form.copy()
        target[y + 2 : y + height - 2, x + 2 : x + width - 2] = 255
        paste_x = x + 12
        paste_y = y + (height - prepared.shape[0]) // 2
        target[paste_y : paste_y + prepared.shape[0], paste_x : paste_x + prepared.shape[1]] = prepared

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output), target)
        return output

    def paste_image_array(
        self,
        form_path: str | Path,
        overlay: np.ndarray,
        output_path: str | Path,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> Path:
        form = cv2.imread(str(form_path), cv2.IMREAD_COLOR)
        if form is None:
            raise FileNotFoundError(f"Could not read form image: {form_path}")

        prepared = self._fit_inside(overlay, width - 24, height - 18)
        target = form.copy()
        target[y + 2 : y + height - 2, x + 2 : x + width - 2] = 255
        paste_x = x + 12
        paste_y = y + (height - prepared.shape[0]) // 2
        target[paste_y : paste_y + prepared.shape[0], paste_x : paste_x + prepared.shape[1]] = prepared

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output), target)
        return output

    def paste_text(
        self,
        form_path: str | Path,
        output_path: str | Path,
        text: str,
        x: int,
        y: int,
        width: int,
        height: int,
        font_scale: float = 0.75,
        thickness: int = 2,
    ) -> Path:
        form = cv2.imread(str(form_path), cv2.IMREAD_COLOR)
        if form is None:
            raise FileNotFoundError(f"Could not read form image: {form_path}")

        target = form.copy()
        target[y + 2 : y + height - 2, x + 2 : x + width - 2] = 255
        baseline = y + (height + 18) // 2
        cv2.putText(
            target,
            text,
            (x + 16, baseline),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (25, 25, 25),
            thickness,
            cv2.LINE_AA,
        )

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output), target)
        return output

    def mark_omr_answers(
        self,
        form_path: str | Path,
        output_path: str | Path,
        answers: dict[int, str],
        options: tuple[str, ...] = ("A", "B", "C", "D"),
        questions_per_column: int = 4,
    ) -> Path:
        form = cv2.imread(str(form_path), cv2.IMREAD_COLOR)
        if form is None:
            raise FileNotFoundError(f"Could not read form image: {form_path}")

        target = form.copy()
        start_x, start_y = 105, 560
        column_gap = 535
        row_gap = 82
        option_gap = 72
        radius = 11

        for question_number, answer in answers.items():
            column = 0 if question_number <= questions_per_column else 1
            row = question_number - 1 if column == 0 else question_number - questions_per_column - 1
            x = start_x + column * column_gap
            y = start_y + row * row_gap
            option_index = options.index(answer)
            cx = x + 78 + option_index * option_gap
            cy = y + 25
            cv2.circle(target, (cx, cy), radius, (35, 35, 35), -1)

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output), target)
        return output

    def _fit_inside(self, image: np.ndarray, max_width: int, max_height: int) -> np.ndarray:
        scale = min(max_width / image.shape[1], max_height / image.shape[0], 1.0)
        new_size = (max(1, int(image.shape[1] * scale)), max(1, int(image.shape[0] * scale)))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
