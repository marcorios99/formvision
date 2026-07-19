# Plantillas y layouts

Una plantilla define la geometría de una página y el layout define cómo
interpretarla. La nomenclatura objetivo para la imagen base es `template.png`,
pero durante la transición el archivo físico existente sigue siendo
`demo/omr_admission/template/blank.png`.

## Imagen de referencia

La imagen de referencia es el formulario en blanco, sin respuestas de un
estudiante. En el demo actual contiene las marcas de alineamiento, cajas,
etiquetas, burbujas y QR que corresponden al layout.

La ruta equivalente de menor cambio sería:

```text
demo/omr_admission/template/
  template.png   # nombre objetivo; hoy blank.png
  layout.json
```

La alternativa `examples/omr_admission/template/` requiere además reorganizar el
demo y no se realiza en esta fase.

## `layout.json`

El layout cargado por `TemplateLoader` contiene:

```json
{
  "template_id": "synthetic_omr_v1",
  "page_size": {"width": 1240, "height": 1754},
  "fields": []
}
```

Cada field puede definir:

- `id`: identificador estable del campo;
- `label`: etiqueta legible;
- `type`: `qr`, `ocr`, `icr` u `omr`;
- `roi`: `{x, y, width, height}` en coordenadas de la página;
- `validators`: reglas como `required`, `digits:8` o `single_choice`;
- `options`: opciones OMR;
- `demo_value`: valor usado por los motores simulados.

## Campos y ROI

El ROI es un rectángulo relativo a `page_size`, no una coordenada descubierta
automáticamente en cada imagen. `CoordinateMapper` convierte ese rectángulo al
tamaño real de la imagen y recorta el campo antes de pasarlo al extractor.

En el layout del demo hay un campo ICR (`student_code`), campos OCR (`full_name`,
`exam_date`, `signature`) y múltiples campos OMR. El QR se detecta desde la
imagen alineada, aunque su región no se procesa como un extractor de field
normal.

## Edición e inspección

`tools/layout_viewer.html` es un editor standalone de navegador. Permite cargar
una imagen, abrir un JSON, mover/redimensionar ROIs, editar propiedades básicas,
añadir/eliminar fields y guardar o descargar el layout.

La CLI puede dibujar el layout sobre una imagen:

```bash
python -m formvision.cli inspect-layout \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --output data/outputs/layout_preview.png
```

Esta inspección visualiza regiones configuradas; no visualiza alineamiento,
dropout, recortes ni resultados de extractores.

## Relación geométrica y alineamiento

Los formularios scanned pueden tener rotación, desplazamiento y ruido. Para que
los ROIs sigan correspondiendo a la página, `process --align` usa
`PageFrameNormalizer`. Si se proporciona `--template-image`, normaliza contra la
imagen de referencia; si no, usa el tamaño del layout y las marcas de la página.

La imagen de referencia es importante cuando la geometría del formulario debe
ser la autoridad: permite comparar la posición del page frame real con el frame
esperado, en vez de confiar únicamente en que la imagen tenga ya el tamaño
correcto. La corrección de perspectiva genérica actual es todavía una primitive
limitada y el flujo está orientado a formularios sintéticos con marcadores.

## Prueba del layout

El recorrido recomendado es:

```text
imagen de referencia
→ layout base
→ campos y ROI
→ inspect-layout
→ process sobre una imagen scanned
```

No existe todavía validación automática de geometría, comparación de campos con
`expected/` ni visualización completa de etapas. Esas capacidades pertenecen a
hitos posteriores.

## Transición de nomenclatura

No se ha renombrado `blank.png` ni se han cambiado sus referencias en código. La
migración futura debe actualizar al menos `README.md`, `docs/flow.md`,
`demo/omr_admission/README.md`, `scripts/build_student_batch.py` y
`scripts/build_digit_overlay_example.py`, además de cualquier ruta aprobada si
el demo se mueve a `examples/`.
