# Modelos y motores

FormVision tiene tres categorías de motores: ICR real pequeño basado en MNIST,
OCR real opcional pretrained y motores demo simulados. Solo los dos primeros
requieren dependencias o artefactos adicionales.

## ICR: dígitos manuscritos

El campo ICR del demo está limitado a dígitos separados dentro de un ROI
numérico. `DigitSegmenter` localiza componentes de foreground, los ordena de
izquierda a derecha y normaliza cada candidato a 28x28.

`MnistDigitIcrEngine` carga `formvision/models/mnist_digit_prototypes.npz`.
Conserva prototipos y muestras normalizadas, compara cada candidato con vecinos
cercanos y agrega puntuaciones por etiqueta. El resultado contiene la secuencia
predicha, confianza, cajas y número de segmentos.

### Preparación y evaluación actuales

Con MNIST IDX disponible bajo `data/external/mnist`:

```bash
python training/train_mnist_digit.py
```

Esto crea el modelo `.npz`; no entrena una red neuronal. La evaluación actual es
por un solo ROI:

```bash
python training/evaluate_icr.py \
  --image demo/omr_admission/images/clean/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --field-id student_code
```

El evaluador imprime valor, confianza y metadata. No calcula exactitud contra
`expected/`. `training/train_digit_sequence.py` es solamente un stub para una
futura ruta CNN/CTC y no debe describirse como entrenamiento implementado.

### Limitaciones ICR

No resuelve dígitos tocándose, cursiva, escritura arbitraria ni secuencias que
requieran comprender el campo completo. El modelo es adecuado para una
demostración controlada y no es un modelo general de handwriting.

## OCR: texto impreso

`DoctrOcrEngine` es un adaptador opcional a docTR. Usa un detector `fast_tiny` y
un recognizer `crnn_mobilenet_v3_small` por defecto, con páginas rectas
asumidas. docTR usa pesos pretrained y los descarga/cachea en
`formvision/models/doctr_cache` durante el primer uso.

No existe entrenamiento OCR local en `training/`. La evaluación disponible
procesa un ROI e imprime valor, confianza y metadata:

```bash
python -m pip install -e ".[ocr]"
python training/evaluate_ocr.py \
  --image demo/omr_admission/images/clean/student_001.png \
  --layout demo/omr_admission/template/layout.json \
  --field-id full_name
```

OCR es opcional y no es requisito para ejecutar la demo con motores simulados.

## Motores simulados

`DemoOcrExtractor` y `DemoIcrExtractor` implementan las interfaces de OCR e ICR
sin reconocer la imagen. Reciben `demo_value` desde el field del layout y lo
devuelven; si el valor es `None`, usan valores de ejemplo predeterminados.

Estos motores sirven para probar carga, ordenamiento, validación y exportación
del pipeline sin modelos. Sus valores no deben presentarse como reconocimiento
real ni utilizarse para medir OCR/ICR.

## Separación de responsabilidades

La generación sintética puede usar MNIST como fuente visual de dígitos, pero eso
no equivale a entrenar el modelo ICR. El entrenamiento ICR y la configuración
OCR son recorridos avanzados opcionales; el flujo principal con `process` puede
ejecutarse con los motores demo y dependencias base.
