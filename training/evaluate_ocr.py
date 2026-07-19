import argparse

import cv2

from formvision.extractors.ocr import DoctrOcrEngine
from formvision.layout.coordinate_mapper import CoordinateMapper
from formvision.layout.template_loader import TemplateLoader


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate docTR OCR on one configured field.")
    parser.add_argument("--image", required=True)
    parser.add_argument("--layout", required=True)
    parser.add_argument("--field-id", default="full_name")
    parser.add_argument("--det-arch", default="fast_tiny")
    parser.add_argument("--reco-arch", default="crnn_mobilenet_v3_small")
    args = parser.parse_args()

    image = cv2.imread(args.image, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(args.image)

    template = TemplateLoader().load(args.layout)
    field = next((item for item in template.fields if item.id == args.field_id), None)
    if field is None:
        raise ValueError(f"Field not found in layout: {args.field_id}")

    roi = CoordinateMapper().crop_field(image, field, template.page_width, template.page_height)
    extraction = DoctrOcrEngine(det_arch=args.det_arch, reco_arch=args.reco_arch).extract(roi)
    print(f"value={extraction.value}")
    print(f"confidence={extraction.confidence:.4f}")
    print(f"metadata={extraction.metadata}")


if __name__ == "__main__":
    main()
