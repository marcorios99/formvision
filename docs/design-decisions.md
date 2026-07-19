# Design Decisions

## Synthetic Public Demo

The repository uses synthetic forms and generated student data so the project can
show document-processing architecture without exposing private forms, production
schemas or proprietary model artifacts.

## Root-Level Demo Folder

The curated portfolio flow lives under `demo/omr_admission`. This keeps the
story clear: template, images, expected values and results are together.

The `data` folder is reserved for external datasets, generated digit snippets
and scratch outputs.

## Constrained ICR First

The first ICR engine targets separated handwritten numeric fields. It segments
foreground components, normalizes each candidate and classifies digits with a
small MNIST-derived model.

This is intentionally simpler than a full sequence model, but easier to explain,
test and maintain for a controlled form demo.

## Optional OCR

docTR is optional because it adds heavier dependencies and downloads pretrained
weights. The default pipeline still runs with deterministic demo OCR.
