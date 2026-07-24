# FormVision

FormVision es un proyecto demostrativo de procesamiento de formularios con
OpenCV. Muestra cómo un formulario puede pasar por un pipeline configurable que
localiza un QR, recorta campos, aplica extractores OCR/ICR/OMR, valida valores y
exporta un resultado estructurado.

Todo el material del repositorio es sintético o público: formularios generados,
identidades ficticias, respuestas ficticias, datos de ground truth y un modelo ICR
pequeño derivado de MNIST. No representa datos reales, reglas de negocio,
precisión productiva ni modelos privados.

## Qué demuestra

- **QR**: lectura mediante el detector QR de OpenCV.
- **OMR**: selección de burbujas mediante puntuación de píxeles.
- **OCR**: lectura de texto impreso; el adaptador real opcional usa docTR.
- **ICR**: lectura acotada de dígitos manuscritos separados; el motor real usa
  segmentación y un modelo pequeño basado en MNIST.

El pipeline también incluye validación y exportación JSON, CSV o SQLite. El
Core requiere motores OCR e ICR configurados explícitamente: los extractores
reciben únicamente el ROI y no existen adaptadores simulados.

## Estado actual

Funcionan la generación sintética, la simulación de escaneos, el procesamiento
individual por CLI, la alineación del page frame, QR/OMR, el ICR MNIST opcional y
el adaptador OCR docTR opcional. La comparación automática con `ground_truth/`, la
evaluación del lote y `demo.py` ya están disponibles; la visualización de etapas
sigue pendiente.

El flujo conceptual que se quiere consolidar es:

```text
template.png
→ definición de campos en layout.json
→ lote de formularios scanned
→ alineamiento contra la plantilla
→ extracción QR / OCR / ICR / OMR
→ comparación con ground_truth
→ reporte JSON de evaluación
```

La imagen de referencia utilizada por el demo es
`demo/omr_admission/template/template.png`.

## Instalación mínima

Se requiere Python >= 3.10:

```bash
python -m pip install -e ".[dev]"
```

`python demo.py` requiere el modelo ICR ya generado en
`formvision/models/mnist_digit_prototypes.npz` y el extra OCR:

```bash
python -m pip install -e ".[ocr]"
```

Genera el modelo ICR con `python training/train_mnist_digit.py`; el entrenamiento
requiere los archivos IDX de MNIST bajo `data/external/mnist` y no los descarga
automáticamente. El extra `mnist` instala Torch/torchvision para tareas
opcionales relacionadas con MNIST, pero no es necesario para inferir el `.npz`
ya generado. docTR descarga o utiliza pesos pretrained en su cache durante el
primer uso.

## Ejemplo mínimo actual

El recorrido principal procesa los diez formularios scanned, los alinea contra
la plantilla y escribe `data/outputs/demo/report.json`:

```bash
python demo.py
```

QR y OMR se comparan con `ground_truth/`. OCR se ejecuta con docTR e ICR con el
modelo MNIST preparado; sus resultados se registran, pero todavía no se puntúan.
El reporte HTML y las visualizaciones de etapas pertenecen a hitos posteriores.

El repositorio ya contiene muestras preparadas. Para procesar el layout completo
desde la CLI se deben configurar los motores reales:

```bash
python -m formvision.cli process \
  --image demo/omr_admission/images/scanned/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --align \
  --template-image demo/omr_admission/template/template.png \
  --icr-engine mnist \
  --ocr-engine doctr \
  --json-output data/outputs/student_001_result.json
```

Un layout que solo contenga QR/OMR puede procesarse sin esos flags. La demo
`python demo.py` configura exclusivamente los motores reales. Los layouts
describen las ROIs y reglas de extracción; los valores conocidos permanecen en
`ground_truth/`. El resultado de la CLI
contiene QR, fields, confianza, validaciones y metadata, pero no se compara automáticamente con
`demo/omr_admission/ground_truth/student_001.json`.

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
