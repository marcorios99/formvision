import cv2
import numpy as np

from formvision.config.schema import FieldConfig, Rect


class CoordinateMapper:
    """Maps template coordinates to the current image dimensions."""

    def scale_rect(
        self,
        rect: Rect,
        template_width: int,
        template_height: int,
        image: np.ndarray,
    ) -> Rect:
        height, width = image.shape[:2]
        return Rect(
            x=round(rect.x * width / template_width),
            y=round(rect.y * height / template_height),
            width=round(rect.width * width / template_width),
            height=round(rect.height * height / template_height),
        )

    def crop_field(
        self,
        image: np.ndarray,
        field: FieldConfig,
        template_width: int,
        template_height: int,
    ) -> np.ndarray:
        rect = self.scale_rect(field.roi, template_width, template_height, image)
        return image[rect.y : rect.y + rect.height, rect.x : rect.x + rect.width]

    def draw_regions(
        self,
        image: np.ndarray,
        fields: tuple[FieldConfig, ...],
        template_width: int,
        template_height: int,
    ) -> np.ndarray:
        preview = image.copy()
        for field in fields:
            rect = self.scale_rect(field.roi, template_width, template_height, image)
            cv2.rectangle(
                preview,
                (rect.x, rect.y),
                (rect.x + rect.width, rect.y + rect.height),
                (0, 120, 255),
                2,
            )
            cv2.putText(
                preview,
                field.id,
                (rect.x, max(20, rect.y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 80, 180),
                1,
                cv2.LINE_AA,
            )
        return preview
