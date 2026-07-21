# Recorridos

FormVision utiliza un entorno sintético para demostrar un pipeline de lectura de
formularios. Los cinco recorridos siguientes separan preparación, uso actual y
trabajo avanzado.

## 1. Preparar la demostración sintética

La preparación completa conceptual es:

```text
plantilla sintética + layout
→ valores ficticios
→ formularios clean
→ variantes scanned
→ expected/
→ modelo ICR MNIST opcional
→ OCR docTR pretrained opcional
```

Con los scripts actuales:

```bash
python scripts/build_student_batch.py
python scripts/build_scanned_variants.py
```

`build_student_batch.py` exporta dígitos MNIST a `data/digits`, recrea la hoja
base y `layout.json`, genera diez formularios clean y escribe un JSON expected por
estudiante más `expected/student_batch.json`. Requiere los archivos IDX de MNIST
aunque no carga el modelo `.npz` de ICR.

`build_scanned_variants.py` aplica rotación, desplazamiento y ruido a los clean y
escribe el lote en `demo/omr_admission/images/scanned/`. Los scanned son la
entrada principal de la demostración; clean es un artefacto de preparación y
depuración.

Para el motor ICR real:

```bash
python training/train_mnist_digit.py
```

Para OCR real opcional:

```bash
python -m pip install -e ".[ocr]"
```

docTR crea el predictor pretrained bajo demanda y cachea sus pesos en
`formvision/models/doctr_cache`.

La demostración ya contiene assets preparados, por lo que esta preparación no es
necesaria para el primer recorrido.

## 2. Ejecutar el flujo principal

El recorrido principal del demo es:

```bash
python demo.py
```

Procesa los diez archivos de `images/scanned/`, los alinea con
`template/template.png`, compara QR y OMR contra `expected/` y escribe
`data/outputs/demo/report.json`. OCR e ICR se registran con motores demo y no
se evalúan; los motores reales son opcionales. El reporte HTML y las
visualizaciones de etapas pertenecen a hitos posteriores.

## 3. Procesar un formulario con la CLI avanzada

Un layout que solo contiene QR/OMR puede ejecutarse con dependencias base. El
layout completo de la demo requiere los motores reales:

```bash
python -m pip install -e ".[dev]"
python -m formvision.cli process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --icr-engine mnist \
  --ocr-engine doctr \
  --json-output data/outputs/student_001_result.json
```

Esto carga el layout, alinea el page frame, elimina guías magenta, intenta leer
QR, extrae OMR y ejecuta los motores configurados para OCR/ICR, valida y escribe
JSON. La CLI del Core no ofrece motores `demo`.

Para activar motores opcionales:

```bash
python -m formvision.cli process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --icr-engine mnist \
  --ocr-engine doctr \
  --json-output data/outputs/student_001_real_engines.json
```

El resultado actual no compara automáticamente con
`demo/omr_admission/expected/student_001.json` y no genera imágenes de etapas.
La comparación es manual y `inspect-layout` solo dibuja las ROIs:

```bash
python -m formvision.cli inspect-layout \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --output data/outputs/layout_preview.png
```

`python scripts/process_demo_batch.py` procesa todos los scanned, pero es una
ruta rígida que duplica `process`, fuerza MNIST y docTR y tampoco compara
`expected/`.

## 4. Crear o editar una plantilla

El recorrido conceptual es:

```text
imagen de referencia
→ layout base
→ definición de campos
→ inspección
→ prueba
```

La herramienta actual es `tools/layout_viewer.html`. Se carga manualmente una
imagen y un JSON; se editan id, label, type y ROI; y se guarda o descarga el JSON.
`python scripts/synthetic_cli.py generate-omr-sheet` puede crear una imagen sintética y su layout como
punto de partida.

Durante esta etapa el archivo físico de la imagen base sigue siendo
`demo/omr_admission/template/template.png`.

Tras guardar el layout, `inspect-layout` permite verificar visualmente las ROIs y
`process` permite probar una imagen. No hay validación geométrica completa ni
detección automática de campos.

## 5. Generar datos sintéticos

La ruta modular de la CLI incluye:

```bash
python scripts/synthetic_cli.py generate-omr-sheet
python scripts/synthetic_cli.py export-mnist-digits
python scripts/synthetic_cli.py compose-digit-strip
python scripts/synthetic_cli.py paste-digit-strip
```

La ruta batch recomendada para los assets existentes es:

```text
template/layout base
→ build_student_batch.py
→ images/clean + expected/
→ build_scanned_variants.py
→ images/scanned
```

La correspondencia clean/scanned/expected se mantiene por nombre de estudiante;
no existe un verificador automático. `build_digit_overlay_example.py` es una
variante ilustrativa y se solapa con el batch.

El batch recrea `template.png` y `layout.json`, por lo que no debe ejecutarse sobre
un layout editado sin conservar una copia previa.

## 6. Entrenar o evaluar modelos

Este recorrido es avanzado y opcional.

```bash
python training/train_mnist_digit.py
python training/evaluate_icr.py \
  --image demo/omr_admission/images/clean/student_001.png \
  --layout demo/omr_admission/template/layout.json
python training/evaluate_ocr.py \
  --image demo/omr_admission/images/clean/student_001.png \
  --layout demo/omr_admission/template/layout.json
```

El entrenamiento produce el modelo de prototipos ICR; el evaluador OCR usa
docTR pretrained. Ambos evaluadores trabajan sobre un ROI y escriben métricas
descriptivas en stdout, pero no comparan contra `expected/` ni producen un
reporte de lote.

## CLI avanzada

Además de `process` e `inspect-layout`, la CLI expone generación de muestras,
hojas OMR, exportación/composición de dígitos y exporters CSV/SQLite. Son
herramientas de preparación o integración; no deben confundirse con el camino
principal para comprender la demo.

## Flujo objetivo

El futuro golden path que se quiere adoptar será:

```bash
python demo.py
```

`demo.py` es una demostración de integración, no un benchmark productivo. Los
artefactos visuales completos y el reporte HTML quedan para hitos posteriores.
