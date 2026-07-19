# OMR Admission Demo

This folder contains the public, portfolio-friendly demo flow.

## Structure

```text
template/
  template.png   Blank answer sheet used by the layout editor.
  layout.json    ROI definitions for QR/OCR/ICR/OMR fields.
images/
  clean/         Generated forms with synthetic student data.
  scanned/       Scan-like variants with rotation, shift and noise.
expected/
  student_batch.json
results/
  Generated processing outputs.
```

## Flow

1. Open `tools/layout_viewer.html`.
2. Load `template/template.png`.
3. Load `template/layout.json`.
4. Adjust ROIs and save the layout JSON.
5. Process one scanned form:

```bash
formvision process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --icr-engine mnist \
  --ocr-engine doctr \
  --json-output data/outputs/student_001_result.json
```

Regenerate the clean and scanned demo images:

```bash
python scripts/build_student_batch.py
python scripts/build_scanned_variants.py
```
