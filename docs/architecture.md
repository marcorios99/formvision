# Arquitectura

FormVision separa el núcleo de procesamiento, la generación sintética, la
preparación de modelos, los assets públicos y las futuras herramientas de
visualización:

```text
formvision/    Núcleo Python: configuración, pipeline, extractores y exporters.
demo/          Assets, evaluación y orquestación de la demostración.
synthetic/     Plantillas, formularios sintéticos, overlays, dígitos y variantes de escaneo.
scripts/       Entrypoints pequeños y recorridos de preparación que consumen las capas correspondientes.
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

`demo.omr_admission.evaluation.demo_batch` es una capa de orquestación separada del
pipeline. Carga el layout y crea el pipeline una sola vez, procesa los diez
scanned, los alinea contra `template/template.png`, compara QR y OMR con
`ground_truth/` y genera `data/outputs/demo/report.json`. Continúa registrando
errores por formulario. OCR e ICR se ejecutan con `DoctrOcrEngine` y
`MnistDigitIcrEngine`, y se incluyen como resultados no evaluados.
No hay reporte HTML ni visualizaciones de etapas en este hito.

## Adaptadores de extracción

- **QR**: `BarcodeExtractor` usa OpenCV sobre la imagen alineada.
- **OMR**: `OmrExtractor` puntúa las opciones configuradas en el ROI.
- **ICR**: requiere un motor configurado explícitamente; `MnistDigitIcrEngine`
  segmenta candidatos y los compara contra muestras y prototipos MNIST.
- **OCR**: requiere un motor configurado explícitamente; `DoctrOcrEngine`
  construye un predictor docTR pretrained.

Los adaptadores temporales `DemoOcrExtractor` y `DemoIcrExtractor` viven bajo
`demo/omr_admission/extractors/` hasta el Hito 3.3, pero `python demo.py` ya no
los utiliza. El Core no usa fallbacks simulados ni los incluye en el paquete
distribuible. `FormProcessingPipeline`
requiere motores OCR/ICR configurados explícitamente
cuando el layout contiene campos de esos tipos, y la CLI del Core solo ofrece
MNIST para ICR y docTR para OCR.
Los motores demo reciben el `demo_value` del field y lo devuelven como valor
simulado. No inspeccionan la imagen para reconocer texto o escritura. Esto hace
posible probar la orquestación sin instalar modelos.

## Fronteras del proyecto

La generación sintética fue retirada de `formvision/layout/` y vive en
`synthetic/`: crea plantillas, formularios clean, overlays, dígitos y variantes
scanned. Los scripts pueden invocar esa lógica, pero no son su ubicación
reutilizable principal. La dirección de dependencias es:

```text
demo ──────────┐
synthetic ─────┼──► formvision
training ──────┤
tools ─────────┘
```

`formvision/` no depende de ninguna de esas capas.

`training/` prepara el modelo ICR de prototipos y ofrece evaluadores por ROI; no
hay entrenamiento OCR local. Los modelos y dependencias opcionales no son
requisitos de layouts que no contienen campos OCR/ICR.

`tools/layout_viewer.html` permite inspeccionar y editar ROIs, pero no visualiza
las etapas internas del pipeline. La evaluación automática del lote escribe JSON;
el reporte HTML sigue siendo un hito posterior.

## Decisiones y limitaciones arquitectónicas

- El entorno completamente sintético permite demostrar arquitectura sin exponer
  formularios, esquemas o datos privados.
- El ICR inicial está deliberadamente limitado a dígitos manuscritos separados.
- docTR es opcional porque añade dependencias pesadas y descarga pesos.
- La alineación está orientada a páginas sintéticas con marcas de referencia.
- La evaluación actual de la demo compara QR y OMR con `ground_truth/`; OCR e ICR
  reales todavía no se evalúan en el lote completo.
- `demo_value` y los extractores simulados temporales permanecen fuera del Core
  hasta el Hito 3.3, aunque ya no sostienen la demo principal.
- La visualización de imágenes intermedias y el reporte HTML aún no existen.
