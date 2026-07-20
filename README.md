# FormVision

FormVision es un proyecto demostrativo de procesamiento de formularios con
OpenCV. Muestra cómo un formulario puede pasar por un pipeline configurable que
localiza un QR, recorta campos, aplica extractores OCR/ICR/OMR, valida valores y
exporta un resultado estructurado.

Todo el material del repositorio es sintético o público: formularios generados,
identidades ficticias, respuestas ficticias, datos `expected/` y un modelo ICR
pequeño derivado de MNIST. No representa datos reales, reglas de negocio,
precisión productiva ni modelos privados.

## Qué demuestra

- **QR**: lectura mediante el detector QR de OpenCV.
- **OMR**: selección de burbujas mediante puntuación de píxeles.
- **OCR**: lectura de texto impreso; el adaptador real opcional usa docTR.
- **ICR**: lectura acotada de dígitos manuscritos separados; el motor real usa
  segmentación y un modelo pequeño basado en MNIST.

El pipeline también incluye validación y exportación JSON, CSV o SQLite. Los
motores `DemoOcrExtractor` y `DemoIcrExtractor` son simuladores: devuelven el
`demo_value` configurado en `layout.json` y sirven para probar la orquestación,
no para demostrar reconocimiento real.

## Estado actual

Funcionan la generación sintética, la simulación de escaneos, el procesamiento
individual por CLI, la alineación del page frame, QR/OMR, el ICR MNIST opcional y
el adaptador OCR docTR opcional. La comparación automática con `expected/`, la
evaluación del lote y `demo.py` ya están disponibles; la visualización de etapas
sigue pendiente.

El flujo conceptual que se quiere consolidar es:

```text
template.png
→ definición de campos en layout.json
→ lote de formularios scanned
→ alineamiento contra la plantilla
→ extracción QR / OCR / ICR / OMR
→ comparación con expected
→ reporte JSON de evaluación
```

La imagen de referencia utilizada por el demo es
`demo/omr_admission/template/template.png`.

## Instalación mínima

Se requiere Python >= 3.10:

```bash
python -m pip install -e ".[dev]"
```

MNIST y docTR son extras, no requisitos del flujo principal:

```bash
python -m pip install -e ".[mnist]"
python -m pip install -e ".[ocr]"
```

MNIST requiere sus archivos IDX bajo `data/external/mnist`; docTR descarga o
utiliza pesos pretrained en su cache durante el primer uso.

## Ejemplo mínimo actual

El recorrido principal procesa los diez formularios scanned, los alinea contra
la plantilla y escribe `data/outputs/demo/report.json`:

```bash
python demo.py
```

QR y OMR se comparan con `expected/`. OCR e ICR usan motores demo en este
recorrido, por lo que se registran pero no se evalúan; los motores reales
siguen siendo opcionales. El reporte HTML y las visualizaciones de etapas
pertenecen a hitos posteriores.

El repositorio ya contiene muestras preparadas. Este comando procesa una imagen
scanned con los extractores demo deterministas y escribe un JSON:

```bash
python -m formvision.cli process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --json-output data/outputs/student_001_result.json
```

Para usar los motores opcionales, se añaden `--icr-engine mnist` y/o
`--ocr-engine doctr`. El resultado contiene QR, fields, confianza, validaciones
y metadata, pero no se compara automáticamente con
`demo/omr_admission/expected/student_001.json`.

## Documentación

- [Recorridos](docs/workflows.md)
- [Plantillas y layouts](docs/templates.md)
- [Datos sintéticos](docs/synthetic-data.md)
- [Modelos y motores](docs/models.md)
- [Arquitectura](docs/architecture.md)

## Limitaciones importantes

- El ICR MNIST requiere dígitos separados dentro de un ROI numérico acotado; no
  resuelve cursiva, dígitos tocándose ni escritura arbitraria.
- No existe entrenamiento OCR local. docTR es pretrained, opcional y puede
  descargar pesos.
- La corrección de perspectiva actual está orientada a las marcas de los
  formularios sintéticos.
- Los resultados sintéticos no son un benchmark de exactitud productiva.
- La visualización completa de etapas y el reporte HTML son trabajo pendiente.

Para ejecutar las pruebas unitarias:

```bash
pytest
```
