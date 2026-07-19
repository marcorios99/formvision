# Synthetic Form Reader

Synthetic Form Reader is a portfolio-friendly Python demo for processing scanned
forms with OpenCV. It reads a QR code, crops configured regions of interest,
extracts OCR/ICR/OMR-style fields, validates the extracted values and exports a
structured result.

The project uses generated forms and public demo layouts only. It does not
include private datasets, production database schemas, proprietary models or
business-specific rules.

## Features

- Synthetic form generation for repeatable demos.
- QR code reading with OpenCV.
- JSON-based layout definitions with explicit ROIs.
- OMR detection for multiple-choice bubbles.
- Optional docTR OCR adapter for printed text fields.
- MNIST-based ICR demo for constrained handwritten numeric fields.
- Synthetic handwritten numeric field for ICR-style demos.
- Field validation rules such as `required`, `digits:8` and `single_choice`.
- JSON, CSV and local SQLite exporters.
- Unit tests for validators, OMR and the pipeline.

## Project Structure

```text
formvision/
  config/            Pipeline settings and layout schema
  image_processing/  Loading, preprocessing and correction primitives
  layout/            Templates, coordinates and synthetic sample generation
  extractors/        QR, OCR, ICR and OMR extractors
  validators/        Field validation rules
  exporters/         JSON, CSV and SQLite outputs
  pipeline/          End-to-end orchestration
  cli.py             Command-line interface

data/
  digits/            MNIST digit PNG samples used to compose ICR fields
  external/          External datasets such as MNIST, ignored by Git
  outputs/           Optional processing outputs, generated on demand

demo/
  omr_admission/     Public end-to-end portfolio demo

scripts/             Demo asset generation scripts
tools/               Standalone layout/result inspection tools
training/            Local OCR/ICR training and evaluation scripts
tests/               Focused automated tests
```

## Quickstart

Install dependencies:

```bash
pip install -e ".[dev]"
```

Optional MNIST support for realistic handwritten digits:

```bash
pip install -e ".[mnist]"
python -c "from torchvision.datasets import MNIST; MNIST(root='data/external/mnist', train=True, download=True)"
```

Train the first supported ICR engine from local MNIST files:

```bash
python training/train_mnist_digit.py
```

Then process a form with the MNIST-based numeric ICR engine:

```bash
python -m formvision.cli process \
  --image demo/omr_admission/images/clean/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --icr-engine mnist
```

Optional docTR OCR support:

```bash
pip install -e ".[ocr]"
```

The default docTR OCR configuration favors speed for straight form fields:

- detector: `fast_tiny`
- recognizer: `crnn_mobilenet_v3_small`
- `assume_straight_pages=True`

The pretrained weights are downloaded by docTR on the first run and cached by
the local project cache under `formvision/models/doctr_cache`.

Generate a synthetic form:

```bash
formvision generate-sample
```

Generate a larger OMR sheet and its matching layout JSON:

```bash
formvision generate-omr-sheet --questions 20 --options A,B,C,D
```

Generate the OMR sheet with MNIST handwritten digits in the ICR field:

```bash
formvision generate-omr-sheet --questions 20 --handwriting-source mnist
```

Generate a random eight-digit ICR value and render each digit from MNIST:

```bash
formvision generate-omr-sheet --handwriting-source mnist --student-code random
```

Build the staged example assets:

```bash
python scripts/build_student_batch.py
```

Create mildly rotated/noisy scan variants:

```bash
python scripts/build_scanned_variants.py
```

Edit a layout visually:

```text
open tools/layout_viewer.html
```

Then load `demo/omr_admission/template/blank.png`, open
`demo/omr_admission/template/layout.json`, adjust the ROIs and use `Save JSON`.
Chrome/Edge can overwrite the selected JSON file after asking for permission.
Other browsers can use `Download JSON`.

The staged example differentiates the technologies:

- `Student Code`: ICR-style handwritten numeric field.
- `Full Name`: OCR-style printed text field.
- `Exam Date`: OCR-style printed date field.
- `Exam Code`: QR code payload.
- `Question 01-08`: OMR marked bubbles.

Generated assets follow this convention:

- `demo/omr_admission/template`: blank form and layout JSON.
- `demo/omr_admission/images/clean`: clean generated student forms.
- `demo/omr_admission/images/scanned`: mildly rotated/noisy scan-like inputs.
- `demo/omr_admission/expected`: synthetic student ground truth.
- `demo/omr_admission/results`: generated processing outputs for the demo.
- `data/digits`: generated MNIST digit snippets.
- `data/outputs`: scratch outputs and experimental generated files.

The current MNIST ICR engine is intentionally scoped to constrained handwritten
numeric fields. It segments separated foreground components, normalizes each
candidate to 28x28 and classifies each digit against an MNIST-derived model. A
future sequence engine could read the full field end-to-end with a CNN/CTC-style
model when touching digits or variable-length handwriting become requirements.

Inspect the configured regions:

```bash
python -m formvision.cli inspect-layout \
  --image demo/omr_admission/images/clean/student_001.png \
  --output data/outputs/layout_preview.png
```

Process the form and export JSON:

```bash
python -m formvision.cli process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --json-output demo/omr_admission/results/student_001_result.json
```

Process with optional MNIST ICR and docTR OCR:

```bash
python -m formvision.cli process \
  --image demo/omr_admission/images/clean/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --icr-engine mnist \
  --ocr-engine doctr \
  --json-output demo/omr_admission/results/student_001_result.json
```

Process every scanned demo image:

```bash
python scripts/process_demo_batch.py
```

Optional CSV and SQLite outputs:

```bash
python -m formvision.cli process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --csv-output demo/omr_admission/results/student_001.csv \
  --sqlite-output demo/omr_admission/results/results.sqlite
```

## Example Output

```json
{
  "document_id": "FORM-2026-0001",
  "template_id": "demo_admission_v1",
  "status": "processed",
  "barcode": {
    "value": "FORM-2026-0001|demo_admission_v1",
    "type": "QR_CODE",
    "confidence": 1.0,
    "source": "opencv_qr"
  },
  "fields": {
    "student_code": {
      "value": "12345678",
      "confidence": 0.82,
      "source": "demo_icr",
      "valid": true,
      "issues": []
    },
    "question_01": {
      "value": "C",
      "confidence": 0.44,
      "source": "omr",
      "valid": true,
      "issues": []
    }
  }
}
```

## Why Synthetic?

The goal is to demonstrate engineering judgment and document-processing
architecture without exposing real forms, model artifacts, coordinate systems,
database structures or production validation logic.

The OMR sheet generator creates an original demo form with magenta answer
bubbles, a synthetic handwritten numeric field and matching JSON coordinates.
It is inspired by common answer-sheet patterns, but it does not reuse
third-party forms or private production templates.

## Documentation

- [Architecture](docs/architecture.md)
- [Processing Flow](docs/flow.md)
- [Design Decisions](docs/design-decisions.md)
- [Limitations](docs/limitations.md)

## Tests

```bash
pytest
```

## Future Improvements

- Add a real OCR adapter such as Tesseract, EasyOCR or another local engine.
- Add optional 1D barcode support through `pyzbar`.
- Add marker-based perspective correction.
- Add a small web viewer for layout inspection and result review.
