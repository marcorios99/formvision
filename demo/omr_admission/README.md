# OMR Admission Demo

Esta carpeta contiene los assets sintéticos de la demostración pública de
FormVision. El flujo detallado está en [docs/workflows.md](../../docs/workflows.md).

## Estructura

```text
template/
  template.png   Imagen de referencia para el alineamiento.
  layout.json    Definición de campos y ROIs.
images/clean/
  Formularios sintéticos limpios para preparación y depuración.
images/scanned/
  Variantes con ruido, rotación y desplazamiento; entrada principal del demo.
expected/
  Ground truth sintético por formulario y manifest del lote.
```

`template/template.png` es la referencia geométrica contra la que se alinean los
formularios de `images/scanned/`.

## Procesar una muestra

```bash
formvision process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --json-output data/outputs/student_001_result.json
```
