# Processing Flow

The public demo flow starts in `demo/omr_admission`.

1. Open `tools/layout_viewer.html`.
2. Load `demo/omr_admission/template/template.png`.
3. Load `demo/omr_admission/template/layout.json`.
4. Adjust and save ROIs.
5. Generate clean forms with `python scripts/build_student_batch.py`.
6. Generate scan-like variants with `python scripts/build_scanned_variants.py`.
7. Process one scanned form:

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

The output contains the barcode, extracted fields, confidence values,
validation issues and processing metadata.
