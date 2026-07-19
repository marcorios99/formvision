# Recorridos actuales de FormVision

Este documento describe el estado observado en `README.md`, `pyproject.toml`,
`formvision/`, `scripts/`, `training/`, `tools/`, `demo/`, `tests/` y `docs/`.
No propone cambios de implementación. Las rutas y comandos son los que existen
actualmente; cuando un paso es una inferencia o tiene una conexión incompleta se
indica como tal.

## Inventario maestro

| Archivo o comando | Propósito | Entradas requeridas | Archivos o resultados producidos | Dependencias necesarias | ¿Modelo entrenado? | Recorrido / función | Dependencias de otros scripts | Duplicado, experimental o incompleto |
|---|---|---|---|---|---|---|---|---|
| `pip install -e ".[dev]"` | Instalar el paquete en editable y las pruebas | Python >= 3.10, repositorio | Entorno Python instalado | `numpy`, `opencv-python`, `pillow`, `qrcode`, `pytest` | No | Uso normal / evaluación | Ninguna | Camino de instalación documentado |
| `pip install -e ".[mnist]"` + descarga de MNIST con `torchvision` | Preparar datos y librerías para ICR y generación con dígitos reales | Red o archivos IDX de MNIST | `data/external/mnist/MNIST/raw/*` | `torch`, `torchvision` | Es el dataset, no un modelo | Generación sintética / configuración | Habilita `export-mnist-digits`, `train_mnist_digit.py` y `handwriting-source mnist` | Opcional; no es requisito de la demo determinista |
| `pip install -e ".[ocr]"` | Habilitar el adaptador docTR | Python y red en el primer uso | Pesos en `formvision/models/doctr_cache` | `python-doctr[torch]` y sus dependencias | Usa pesos pretrained, no modelo local entrenado | Configuración / evaluación | `process --ocr-engine doctr`, `process_demo_batch.py`, `evaluate_ocr.py` | Opcional y pesado |
| `formvision generate-sample` | Crear una muestra desde un layout existente | `demo/omr_admission/template/layout.json` por defecto | `data/outputs/sample_001.png` por defecto | Dependencias base; OpenCV | No | Uso normal / generación sintética | `TemplateLoader`, `SyntheticFormFactory` | Variante corta y poco conectada al demo de 10 estudiantes |
| `formvision generate-omr-sheet` | Crear una hoja OMR y su layout JSON | Parámetros CLI; opcionalmente MNIST para `--handwriting-source mnist` | PNG y JSON, por defecto en `data/outputs/` | Base; MNIST solo con fuente `mnist` | No con `opencv`; no con MNIST como modelo | Creación de plantillas / generación sintética | `SyntheticOmrSheetFactory`, `TemplateLoader` indirectamente | Principal generador reutilizable |
| `formvision export-mnist-digits` | Exportar PNGs normalizados, agrupados por dígito | IDX de MNIST en `data/external/mnist` | `data/digits/0..9/*.png` | `[mnist]`/archivos IDX | No | Generación sintética / preparación ICR | `MnistDigitExporter` | Paso auxiliar que el batch ejecuta implícitamente |
| `formvision compose-digit-strip` | Componer una tira aleatoria de dígitos | `data/digits/` | `data/outputs/random_digit_strip.png` y valor impreso | Base; PNGs de `export-mnist-digits` | No | Generación sintética | `DigitStripFactory` | Herramienta interna expuesta por CLI |
| `formvision paste-digit-strip` | Pegar una tira en una imagen de formulario | Imagen de formulario y tira, por defecto en `data/outputs/` | `data/outputs/omr_sheet_with_digit_strip.png` | Base; imágenes previas | No | Generación sintética | `FormOverlay` | Paso de bajo nivel; solapado por `build_student_batch.py` |
| `formvision inspect-layout --image ... --layout ...` | Dibujar ROIs sobre una imagen | Imagen y layout JSON | PNG de previsualización, por defecto `data/outputs/layout_preview.png` | Dependencias base | No | Creación de plantillas / inspección | `TemplateLoader`, `CoordinateMapper` | Es visualización de ROIs, no muestra etapas del pipeline |
| `formvision process --image ... --layout ... --align --template-image ...` | Ejecutar el pipeline y exportar resultado | Imagen, layout y referencia de plantilla | JSON; opcional CSV y SQLite | Base; modelo MNIST si `--icr-engine mnist`; docTR si `--ocr-engine doctr` | Solo con ICR MNIST explícito | Uso normal / evaluación | `FormProcessingPipeline`, extractores y exporters | Camino principal; por defecto usa ICR/OCR deterministas basados en `demo_value` |
| `python scripts/build_student_batch.py` | Regenerar plantilla base, 10 formularios limpios y ground truth | MNIST IDX, layout/template de demo | Sobrescribe `template/template.png` y `layout.json`; crea `images/clean/student_*.png`, `expected/student_*.json`, `expected/student_batch.json`; usa `data/digits` | Base + archivos MNIST; no carga un modelo `.npz` | No para producir imágenes; sí requiere datos MNIST | Generación sintética | `MnistDigitExporter`, `SyntheticOmrSheetFactory`, `DigitStripFactory`, `FormOverlay` | Regenera el layout que el usuario podría haber editado; mezcla plantilla y dataset |
| `python scripts/build_scanned_variants.py` | Simular rotación, desplazamiento y ruido | `demo/omr_admission/images/clean/student_*.png` | `images/scanned/student_*.png` | Base, OpenCV | No | Generación sintética | `ScanSimulator` | Paso claro; no produce ground truth nuevo porque conserva el de clean |
| `python scripts/process_demo_batch.py` | Procesar todos los escaneos del demo | `images/scanned/*.png`, layout JSON, modelo MNIST | `data/outputs/demo_batch/student_*_result.json` | Base + `.npz` MNIST + docTR y pesos cacheados | Sí, ICR MNIST; docTR pretrained | Uso normal / evaluación | `TemplateLoader`, `FormProcessingPipeline`, `MnistDigitIcrEngine`, `DoctrOcrEngine` | Duplicado de repetir `formvision process`; más rígido y menos configurable |
| `python scripts/build_digit_overlay_example.py` | Generar una secuencia ilustrativa de overlays | MNIST IDX, template/layout de demo | `data/outputs/digit_overlay_example/*` y metadata JSON; regenera template/layout | Base + MNIST IDX | No | Generación sintética / ejemplo | `MnistDigitExporter`, `DigitStripFactory`, `FormOverlay`, `SyntheticOmrSheetFactory` | Experimental/ilustrativo; se solapa con `build_student_batch.py` |
| `python training/train_mnist_digit.py` | Crear el modelo local de prototipos y muestras MNIST | IDX de entrenamiento | `formvision/models/mnist_digit_prototypes.npz` | Base + NumPy/OpenCV; MNIST descargado | Es el entrenamiento del ICR soportado | Entrenamiento | Consumido por `MnistDigitIcrEngine` y evaluador ICR | Modelo simple de prototipos/k-NN; no entrena OCR |
| `python training/train_digit_sequence.py` | Anunciar la futura ruta de ICR secuencial | Ninguna | Solo mensaje en stdout | Python | No | Entrenamiento | Ninguna | Incompleto: stub/roadmap, no entrena |
| `python training/evaluate_icr.py --image ... --layout ...` | Evaluar un ROI ICR individual | Imagen, layout, `--field-id`; `.npz` por defecto | Valor, confianza y metadata en stdout | Base + `.npz` MNIST | Sí, `.npz` existente | Evaluación | `TemplateLoader`, `CoordinateMapper`, `MnistDigitIcrEngine` | Evaluación aislada; no compara automáticamente con `expected/` |
| `python training/evaluate_ocr.py --image ... --layout ...` | Evaluar un ROI OCR individual con docTR | Imagen, layout, `--field-id` | Valor, confianza y metadata en stdout | Base + `[ocr]` + pesos descargados/cacheados | No entrenado localmente; pretrained | Evaluación | `TemplateLoader`, `CoordinateMapper`, `DoctrOcrEngine` | Evaluación aislada; no produce reporte ni ground truth |
| Abrir `tools/layout_viewer.html` | Editar ROIs y propiedades de fields en el navegador | Imagen template y layout JSON cargados manualmente | JSON guardado con File System Access API o descargado | Navegador moderno; no Python | No | Creación de plantillas | Ningún script; consume el esquema de `layout.json` | Herramienta standalone; no valida el layout contra el pipeline |
| `pytest` | Ejecutar pruebas unitarias | Código fuente y dependencias base/dev | Resultado de pruebas; cachés de pytest/bytecode pueden aparecer | `[dev]` | No | Evaluación técnica | Tests de OMR, pipeline, normalización, simulador, segmentación y validadores | No es evaluación de exactitud contra los archivos de demo |

### Componentes internos que sostienen los comandos

`formvision/cli.py` registra los comandos anteriores. `FormProcessingPipeline`
encadena carga, corrección de perspectiva, alineación opcional, eliminación de
magenta, QR, recorte de ROIs, OMR/OCR/ICR, validación y exportación. Los
extractores por defecto son `DemoOcrExtractor` y `DemoIcrExtractor`: devuelven
el `demo_value` del layout, no leen realmente el texto de la imagen. OMR y QR sí
se calculan desde la imagen.

Los módulos de `formvision/image_processing/` son primitives reutilizables,
pero no tienen comandos propios. `PerspectiveCorrector` es un placeholder que
devuelve la imagen; la alineación efectiva usa `PageFrameNormalizer` cuando se
solicita `--align`. Los exporters JSON/CSV/SQLite son salidas del comando
`process`, no recorridos independientes.

## A. Ejecutar una demostración preparada

### Orden actual

1. Instalar `pip install -e ".[dev]"`.
2. Opcionalmente instalar `[mnist]` y `[ocr]` si se quiere usar la variante
   tecnológica completa descrita en el README.
3. Abrir manualmente `tools/layout_viewer.html` y cargar
   `demo/omr_admission/template/template.png` y `layout.json`.
4. Según `docs/flow.md`, ajustar y guardar ROIs.
5. Ejecutar `python scripts/build_student_batch.py`.
6. Ejecutar `python scripts/build_scanned_variants.py`.
7. Ejecutar `formvision process` sobre un escaneo. El ejemplo documentado usa
   `--icr-engine mnist` y `--ocr-engine doctr`.
8. Alternativamente ejecutar `python scripts/process_demo_batch.py` para los 10
   escaneos.

### Comandos, entradas y salidas

```bash
pip install -e ".[dev]"
python scripts/build_student_batch.py
python scripts/build_scanned_variants.py
formvision process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --icr-engine mnist \
  --ocr-engine doctr \
  --json-output data/outputs/student_001_result.json
```

Entradas: template/layout, MNIST raw para regenerar assets, imagen escaneada y
modelo MNIST; docTR requiere además sus pesos. Salida: un JSON estructurado con
QR, fields, confidence, validación y metadata. CSV/SQLite son opcionales.

### Desorden y conexiones débiles

- La demostración preparada ya contiene `template.png`, `layout.json`, 10 imágenes
  clean, 10 escaneos y expected/results; regenerar no es necesario para entender
  el proyecto.
- `build_student_batch.py` vuelve a crear la plantilla y el layout, incluso si
  antes se editaron con el viewer. El orden “editar y luego regenerar” puede
  borrar el trabajo de layout.
- El camino narrado exige MNIST y docTR, pero el README dice correctamente que
  no son obligatorios para ejecutar el pipeline: el default es demo/determinista.
- `process_demo_batch.py` es otra ruta para lo mismo y fija MNIST/docTR; no acepta
  argumentos ni `--json-output`.
- El pipeline no guarda imágenes de alineación, dropout, ROIs ni recortes. La
  única imagen visual que produce la CLI es `inspect-layout`, que dibuja ROIs;
  no existe una visualización de etapas.
- No hay comparación automática entre `data/outputs/` y `expected/`; el usuario debe
  inspeccionar JSON manualmente.

### Recorrido simplificado propuesto

Para una persona que solo clonó el repositorio: instalar `[dev]`, usar los assets
ya presentes, ejecutar `formvision process` con defaults sobre un clean o scanned,
abrir el JSON y luego ejecutar `inspect-layout` si necesita entender las ROIs.
La variante MNIST/docTR debe quedar como una segunda demostración opcional.

## B. Crear una nueva plantilla

### Orden actual

La ruta visual existente es:

1. Partir de una imagen en blanco.
2. Abrir `tools/layout_viewer.html`.
3. Cargar la imagen y un JSON existente (normalmente el layout demo).
4. Mover, redimensionar, crear o eliminar fields; editar id, label, type, ROI.
5. Guardar el JSON con `Save JSON` o descargarlo con `Download JSON`.
6. Usar el JSON en `formvision process` o inspeccionarlo con
   `formvision inspect-layout`.

También existe `formvision generate-omr-sheet`, que genera simultáneamente una
imagen y un layout sintético. `build_student_batch.py` y
`build_digit_overlay_example.py` invocan el mismo factory y escriben
`demo/omr_admission/template/template.png` y `layout.json`, por lo que son
generadores de plantilla además de generadores de datos.

### Entradas y salidas

Entrada principal: formulario blanco y, para editar desde cero, un JSON base con
`template_id`, `page_size` y `fields`; el viewer no crea un layout vacío antes de
cargarlo. Salida: layout JSON con ROIs y tipos `qr`, `ocr`, `icr`, `omr`.

```bash
formvision inspect-layout \
  --image path/to/template.png \
  --layout path/to/layout.json \
  --output data/outputs/layout_preview.png
```

### Sobrantes, duplicados y desconexiones

- No hay un comando “crear layout desde imagen blanca”; el viewer depende de un
  JSON existente o de la generación sintética.
- El viewer permite editar `validators` solo indirectamente: no ofrece controles
  para ellos, aunque el JSON sí los soporta.
- No existe validación de geometría, detección de campos ni prueba de extracción
  desde el viewer.
- Generar con `build_student_batch.py` después de editar contradice el objetivo de
  edición, porque restaura posiciones y valores.

### Recorrido simplificado propuesto

Imagen blanca → generar una sola vez un layout base con
`generate-omr-sheet --blank-answers` (si el formulario es sintético) o conservar
un JSON base → editar/guardar en el viewer → comprobar con `inspect-layout` →
procesar una imagen de prueba. Para una plantilla real, el paso de generación
sintética no aplica y debe comenzar con un JSON base preparado manualmente.

## C. Generar datos sintéticos

### Orden actual

La ruta de batch es:

1. MNIST raw disponible.
2. `build_student_batch.py` exporta 12 PNG por dígito a `data/digits`.
3. El mismo script recrea `template.png` y `layout.json` con ocho preguntas y
   campos vacíos.
4. Genera 10 clean forms aplicando tira de dígitos, textos y respuestas OMR.
5. Escribe un JSON esperado por estudiante y `student_batch.json`.
6. `build_scanned_variants.py` lee clean y escribe variantes con rotación,
   desplazamiento y ruido.

La CLI ofrece la ruta más modular: `generate-omr-sheet`, `export-mnist-digits`,
`compose-digit-strip` y `paste-digit-strip`. `build_digit_overlay_example.py`
es una variante ilustrativa de un solo formulario.

### Entradas y salidas

Entradas: MNIST raw si se usan dígitos realistas, parámetros sintéticos y una
plantilla/layout existente. Salidas: formulario limpio, variantes escaneadas,
ground truth por muestra, manifest, PNGs de dígitos y, en la variante ilustrativa,
metadata de los overlays.

### Sobrantes, duplicados y desconexiones

- `build_student_batch.py` y `build_digit_overlay_example.py` repiten la misma
  cadena de exportar dígitos → crear hoja → aplicar overlays.
- `generate-omr-sheet --handwriting-source mnist` usa MNIST directamente para
  renderizar la hoja, mientras el batch exporta PNGs y luego compone tiras; son
  dos mecanismos distintos para ICR sintético.
- `compose-digit-strip` y `paste-digit-strip` exponen operaciones internas que el
  batch ya encapsula.
- La simulación no copia ni transforma `expected/`: la correspondencia se asume
  por nombre de archivo, no se verifica en código.
- El generador acepta más preguntas, pero el batch fija ocho y sus overlays usan
  coordenadas fijas; no es un generador general de datasets.

### Recorrido simplificado propuesto

MNIST opcional → `generate-omr-sheet` para obtener template + layout → un único
generador parametrizable para clean + expected → `build_scanned_variants.py` →
dataset con clean/scanned/expected alineados por nombre.

## D. Entrenar o configurar modelos

Este recorrido no es requisito para la demo determinista.

### OCR

No hay entrenamiento OCR local. `pip install -e ".[ocr]"` configura docTR; al
crear `DoctrOcrEngine`, se construye un predictor pretrained con arquitecturas
`fast_tiny` y `crnn_mobilenet_v3_small`, y los pesos se descargan/cachean en el
primer uso. `training/evaluate_ocr.py` ejecuta un único ROI y solo imprime valor,
confianza y metadata.

### ICR

1. Descargar o colocar los IDX de MNIST bajo `data/external/mnist/MNIST/raw`.
2. Ejecutar `python training/train_mnist_digit.py`.
3. Obtener `formvision/models/mnist_digit_prototypes.npz`.
4. Evaluar un campo con `training/evaluate_icr.py` o usarlo en
   `formvision process --icr-engine mnist`.

El archivo de entrenamiento crea prototipos promedio y conserva muestras para
vecinos más cercanos; no es un entrenamiento de red neuronal. `train_digit_sequence.py`
solo imprime que el futuro modelo CNN/CTC aún no existe.

### Sobrantes y desconexiones

- README llama “train” a la creación de un modelo de prototipos, pero no hay
  entrenamiento OCR equivalente.
- Los evaluadores no reciben ground truth ni calculan CER/WER, exactitud,
  precisión o recall; son smoke tests de un campo.
- La demo puede usar el `.npz` ya presente, por lo que entrenar de nuevo cambia
  reproducibilidad sin ser necesario.

### Recorrido simplificado propuesto

Configurar MNIST/docTR solo si se desea evaluar un motor real → generar o escoger
una muestra → entrenar únicamente el prototipo ICR → evaluar ICR/OCR por ROI →
integrar el motor explícitamente en `process`. Mantener el camino default demo
separado.

## E. Evaluar el pipeline

### Orden actual

Hay tres niveles distintos:

1. `pytest` comprueba componentes y dos casos del pipeline con formularios
   sintéticos temporales.
2. `training/evaluate_icr.py` y `training/evaluate_ocr.py` procesan un solo ROI.
3. `formvision process` o `scripts/process_demo_batch.py` procesa una o todas las
   muestras y serializa resultados.

Para muestras del demo, el orden práctico es:

```bash
formvision process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --json-output data/outputs/student_001_result.json

# Opcionalmente, para el motor MNIST/docTR:
python training/evaluate_icr.py \
  --image demo/omr_admission/images/clean/student_001.png \
  --layout demo/omr_admission/template/layout.json
python training/evaluate_ocr.py \
  --image demo/omr_admission/images/clean/student_001.png \
  --layout demo/omr_admission/template/layout.json
```

### Entradas y salidas

Entradas: imagen clean o scanned, layout y opcionalmente modelo/docTR. Salidas:
JSON/CSV/SQLite del pipeline o líneas de stdout de los evaluadores. `expected/`
contiene los valores sintéticos por muestra, pero ningún comando actual los lee
para comparar.

### Sobrantes, duplicados y desconexiones

- `process_demo_batch.py` repite el procesamiento de la CLI y fija dependencias
  pesadas.
- `evaluate_icr.py`/`evaluate_ocr.py` recortan y extraen, pero quedan fuera de la
  validación, barcode, OMR y exportación de resultados.
- `pytest` y la evaluación del demo miden cosas distintas: no hay un reporte
  único que combine regresión unitaria, resultado predicho y ground truth.
- `--align` normaliza el page frame, pero no expone la imagen alineada ni sus
  etapas intermedias.
- La comparación manual puede revelar que un resultado tenga `processed` aun
  cuando el valor no coincida con `expected`; las validaciones solo comprueban
  reglas del layout, no la verdad esperada.

### Recorrido simplificado propuesto

Escoger muestra + expected → ejecutar una única entrada (`process`) con motor
explícito → guardar JSON → comparar automáticamente fields con expected → emitir
resumen por muestra y, opcionalmente, imágenes de alineación/ROIs/recortes.
Hasta que exista esa comparación, el paso final debe ser manual.

## Golden path propuesto para la demo

El recorrido más corto y reproducible para comprender el proyecto, sin convertir
modelos opcionales en prerequisito, es:

```text
pip install -e ".[dev]"
  → formvision process --image demo/omr_admission/images/scanned/student_001.png \
       --layout demo/omr_admission/template/layout.json \
       --align --template-image demo/omr_admission/template/template.png \
       --json-output data/outputs/student_001_result.json
  → abrir data/outputs/student_001_result.json
  → formvision inspect-layout --image demo/omr_admission/images/scanned/student_001.png \
       --layout demo/omr_admission/template/layout.json \
       --output data/outputs/layout_preview.png
  → visualizar la imagen con ROIs y el JSON resultante
  → comparar manualmente con demo/omr_admission/expected/student_001.json
```

En términos de la secuencia solicitada:

```text
instalar → ejecutar un comando → abrir la demo → procesar muestra → visualizar etapas → comparar resultado
```

La parte “visualizar etapas” no está implementada literalmente: actualmente
`inspect-layout` solo visualiza regiones configuradas. Por eso el golden path usa
esa inspección como sustituto documentado y deja constancia de que no hay una
vista de etapas del pipeline.

## Resumen final

### 1. Resumen de los recorridos encontrados

- A: demo pre-generada, con una ruta simple por CLI y otra batch con modelos.
- B: edición manual de ROIs en HTML o generación sintética de imagen + layout.
- C: MNIST → clean + expected → variantes scanned; con dos implementaciones
  paralelas de overlays.
- D: prototipo ICR local y configuración/evaluación docTR; no entrenamiento OCR.
- E: tests unitarios, evaluadores por ROI y procesamiento completo, sin métrica
  automática contra ground truth.

### 2. Principales fuentes de desorden

- La documentación mezcla demo ya preparada con regeneración de assets.
- Los defaults deterministas y la ruta MNIST/docTR cuentan historias distintas.
- Los generadores batch recrean el layout y pueden borrar una edición manual.
- Las salidas están distribuidas entre `demo/`, `data/outputs/` y el cache de
  modelos.
- No existe visualización de etapas ni comparación automática con `expected/`.

### 3. Comandos redundantes o demasiado internos

`process_demo_batch.py` duplica `formvision process`; `build_digit_overlay_example.py`
duplica gran parte de `build_student_batch.py`; `compose-digit-strip` y
`paste-digit-strip` exponen primitivas que ya usa el batch. `train_digit_sequence.py`
es incompleto y los dos `evaluate_*.py` son evaluadores aislados, no una evaluación
del pipeline entero.

### 4. Dependencias reales de la demo

Para procesar los assets existentes con los extractores default: Python >= 3.10,
dependencias base de `pyproject.toml`, el layout JSON y una imagen. Para la ruta
documentada con motores reales: además `formvision/models/mnist_digit_prototypes.npz`,
`python-doctr[torch]` y sus pesos cacheados/descargables. MNIST raw es necesario
para regenerar el batch, no para leer los assets ya presentes.

### 5. Propuesta del golden path

Instalar `[dev]` → ejecutar una vez `formvision process` con un scanned existente y
`--align` → abrir el resultado y el demo → ejecutar `inspect-layout` para la
visualización disponible → comparar manualmente con `expected/student_001.json`.
La variante MNIST/docTR queda fuera del camino inicial.

### 6. `git diff --stat`

En el entorno analizado no existe `.git` en la raíz del repositorio, por lo que
`git diff --stat` no puede ejecutarse aquí y devuelve `fatal: not a git repository`.
La verificación de archivos se hizo con el estado del sistema de archivos; este
análisis creó únicamente este documento.
