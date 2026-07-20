# Arquitectura

FormVision separa el núcleo de procesamiento, la generación sintética, la
preparación de modelos, los assets públicos y las futuras herramientas de
visualización:

```text
formvision/    Núcleo Python: configuración, pipeline, extractores y exporters.
demo/          Assets sintéticos preparados para la demostración.
scripts/       Generación de lotes, escaneos y ejemplos.
training/      Preparación y evaluación local de ICR/OCR.
tools/         Herramientas standalone; actualmente editor HTML de layouts.
data/          MNIST externo, dígitos generados y salidas de trabajo.
docs/          Contratos y recorridos documentales.
```

## Pipeline actual

`FormProcessingPipeline.process(...)` ejecuta conceptualmente:

1. `ImageLoader` carga la imagen.
2. `PerspectiveCorrector` aplica la corrección disponible; en el estado actual
   es una primitive que conserva la imagen.
3. Si `align=True`, `PageFrameNormalizer` normaliza el page frame. Puede usar
   una imagen de referencia mediante `template_image_path` o las dimensiones y
   marcas del layout.
4. `MagentaDropout` elimina las guías magenta de la imagen alineada.
5. `BarcodeExtractor` intenta leer el QR.
6. `TemplateLoader` convierte `layout.json` en un `FormTemplate`; cada field
   contiene tipo, ROI, validadores, opciones y opcionalmente `demo_value`.
7. `CoordinateMapper` recorta cada ROI con relación a `page_size`. Los fields se
   procesan en orden OMR, ICR y OCR.
8. El extractor correspondiente produce valor, confianza, origen y metadata.
9. `FieldValidator` aplica reglas como `required`, `digits:8` y
   `single_choice`.
10. `FormProcessingResult` reúne QR, fields, estado y metadata.
11. `JsonExporter` siempre escribe JSON; CSV y SQLite son salidas opcionales de
    la CLI.

La CLI expone este pipeline como `formvision process` o
`python -m formvision.cli process`.

## Evaluación del demo

`formvision.evaluation.demo_batch` es una capa de orquestación separada del
pipeline. Carga el layout y crea el pipeline una sola vez, procesa los diez
scanned contra la plantilla, compara QR y OMR con `expected/` y genera
`data/outputs/demo/report.json`. OCR e ICR se incluyen como resultados no
evaluados porque los motores base son demostrativos; los motores reales siguen
siendo opcionales. No hay reporte HTML ni visualizaciones de etapas en este
hito.

## Adaptadores de extracción

- **QR**: `BarcodeExtractor` usa OpenCV sobre la imagen alineada.
- **OMR**: `OmrExtractor` puntúa las opciones configuradas en el ROI.
- **ICR**: por defecto `DemoIcrExtractor`; opcionalmente
  `MnistDigitIcrEngine` segmenta candidatos y los compara contra muestras y
  prototipos MNIST.
- **OCR**: por defecto `DemoOcrExtractor`; opcionalmente `DoctrOcrEngine`
  construye un predictor docTR pretrained.

Los motores demo reciben el `demo_value` del field y lo devuelven como valor
simulado. No inspeccionan la imagen para reconocer texto o escritura. Esto hace
posible probar la orquestación sin instalar modelos.

## Fronteras del proyecto

La generación sintética en `formvision/layout/` y `scripts/` crea plantillas,
formularios clean, variantes scanned y ground truth. No forma parte del núcleo
de extracción, aunque produce sus entradas.

`training/` prepara el modelo ICR de prototipos y ofrece evaluadores por ROI; no
hay entrenamiento OCR local. Los modelos y dependencias opcionales no son
requisitos del pipeline con motores demo.

`tools/layout_viewer.html` permite inspeccionar y editar ROIs, pero no visualiza
las etapas internas del pipeline. La evaluación automática del lote escribe JSON;
el reporte HTML sigue siendo un hito posterior.

## Decisiones y limitaciones arquitectónicas

- El entorno completamente sintético permite demostrar arquitectura sin exponer
  formularios, esquemas o datos privados.
- El ICR inicial está deliberadamente limitado a dígitos manuscritos separados.
- docTR es opcional porque añade dependencias pesadas y descarga pesos.
- La alineación está orientada a páginas sintéticas con marcas de referencia.
- La comparación con `expected/` no pertenece todavía al pipeline implementado;
  debe añadirse como una etapa de evaluación separada.
- La visualización de imágenes intermedias y el reporte HTML aún no existen.
