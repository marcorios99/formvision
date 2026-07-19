# Datos sintéticos

FormVision usa formularios y valores sintéticos para mostrar una arquitectura de
procesamiento sin exponer formularios reales, datos personales, esquemas
productivos o modelos privados. El dataset del demo es reproducible y sirve para
entender el pipeline, no para medir exactitud de producción.

## Preparación de una muestra

La fábrica sintética crea una hoja con QR, campos de texto, un campo numérico
manuscrito simulado y burbujas OMR. `layout.json` se genera junto con la imagen y
contiene las ROIs y, durante la generación, valores de demostración.

El batch `scripts/build_student_batch.py` crea diez estudiantes con nombres,
códigos de ocho dígitos, una fecha y respuestas A/B/C/D deterministas. Escribe:

```text
demo/omr_admission/images/clean/student_001.png ... student_010.png
demo/omr_admission/expected/student_001.json ... student_010.json
demo/omr_admission/expected/student_batch.json
```

También crea `data/digits/0..9/` a partir de MNIST y vuelve a crear la plantilla
base y `layout.json`. Esto significa que el script es una herramienta de
preparación completa, no solo un generador de formularios.

## Clean frente a scanned

Los clean son formularios sintéticos ideales. Se conservan para depurar overlays,
comparar la generación y localizar problemas geométricos.

`scripts/build_scanned_variants.py` lee los clean y aplica la configuración
actual de `ScanSimulator`: hasta 1.5 grados de rotación, hasta 8 píxeles de
desplazamiento y ruido gaussiano con sigma 3.0. Escribe los resultados en:

```text
demo/omr_admission/images/scanned/student_*.png
```

Los scanned son la entrada principal de la demostración porque representan el
material que el pipeline debe procesar. Clean es un artefacto de preparación y
depuración, no el camino final de lectura.

## Ground truth

Por cada clean se escribe un JSON en `expected/` con imagen, código de examen,
código de estudiante, nombre, fecha y respuestas. `student_batch.json` contiene
el manifest completo.

La relación entre scanned y expected se asume por el mismo nombre de estudiante.
El código actual no lee estos archivos para comparar automáticamente con los
resultados; esa evaluación será un hito posterior.

## MNIST opcional

MNIST puede participar de dos formas:

1. `MnistDigitExporter` exporta PNGs normalizados por dígito a `data/digits`, que
   después se usan para componer tiras manuscritas.
2. `generate-omr-sheet --handwriting-source mnist` usa el renderer MNIST
   directamente al dibujar el campo numérico.

Si no se dispone de MNIST, la generación sintética puede usar la fuente OpenCV
por defecto. El batch actual sí invoca la exportación MNIST y por tanto requiere
los archivos IDX bajo `data/external/mnist`.

## Semillas y reproducibilidad

La CLI `generate-omr-sheet` acepta `--seed` y la simulación del batch de escaneos
usa semillas deterministas `1000 + index`. La CLI también permite elegir el
student code o pedir uno aleatorio. `build_student_batch.py` calcula los códigos
y respuestas mediante fórmulas fijas, mientras que sus tiras de dígitos dependen
de la selección disponible en `data/digits`.

## Scripts actuales

- `build_student_batch.py`: plantilla base, clean, expected y manifest.
- `build_scanned_variants.py`: variantes scanned.
- `build_digit_overlay_example.py`: ejemplo ilustrativo de overlays para una
  sola muestra; se solapa con el batch.
- `formvision generate-omr-sheet`: generación modular de imagen + layout.
- `export-mnist-digits`, `compose-digit-strip` y `paste-digit-strip`: operaciones
  auxiliares de bajo nivel.

## Limitaciones

- El generador batch fija ocho preguntas y coordenadas de overlays; no es un
  generador general de cualquier formulario.
- Regenera `template.png` y `layout.json`, por lo que puede sobrescribir una edición
  manual del layout.
- La simulación de escaneo conserva la correspondencia por nombre, pero no
  verifica que expected y resultado sean consistentes.
- Los valores sintéticos no constituyen un benchmark OCR/ICR/OMR.
