# Limitations

- The MNIST ICR engine assumes separated handwritten digits inside a constrained
  numeric ROI.
- Touching digits, cursive text and arbitrary handwriting require a detector or
  a sequence model such as CNN/CTC.
- docTR OCR downloads pretrained weights on first use.
- Perspective correction is currently focused on synthetic/demo forms with page
  frame markers.
- The generated demo data is not a benchmark for production OCR/ICR accuracy.

Future work can add a result viewer, richer layout validation, batch reporting
and a full-field sequence ICR engine.
