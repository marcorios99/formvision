# Architecture

FormVision is split into a reusable processing package, public demo assets and
local tooling.

```text
formvision/    Core Python package.
demo/          Curated portfolio demo assets.
scripts/       Demo asset generation.
training/      Local ICR/OCR model preparation and evaluation.
tools/         Standalone browser tools.
data/          External datasets, generated digit snippets and scratch outputs.
```

The processing pipeline loads an image, optionally normalizes the page frame,
removes magenta guide marks, crops configured ROIs, extracts each field by type,
validates values and exports structured results.

Field extraction is intentionally adapter-based:

- QR: OpenCV QR detector.
- OMR: pixel-based bubble scoring.
- ICR: constrained MNIST numeric engine or deterministic demo engine.
- OCR: docTR adapter or deterministic demo engine.
