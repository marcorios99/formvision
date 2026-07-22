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
ground_truth/
  Ground truth sintético por formulario y manifest del lote.
```

`template/template.png` es la referencia geométrica contra la que se alinean los
formularios de `images/scanned/`.

## Procesar una muestra

Para ejecutar el lote público completo desde la raíz del repositorio:

```bash
python demo.py
```

El comando usa exclusivamente `images/scanned/`, alinea contra
`template/template.png`, compara QR y OMR con `ground_truth/` y escribe
`data/outputs/demo/report.json`. OCR e ICR se registran con motores demo, por
lo que no se evalúan; los motores reales siguen siendo opcionales. El reporte
HTML y las visualizaciones de etapas pertenecen a hitos posteriores.

## Procesar una muestra con la CLI avanzada

```bash
formvision process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --json-output data/outputs/student_001_result.json
```
