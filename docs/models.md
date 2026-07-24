# Modelos y motores

FormVision contiene ICR real pequeño basado en MNIST y OCR real opcional
pretrained. Ambos deben configurarse explícitamente cuando el layout los
requiere.

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
`ground_truth/`. `training/train_digit_sequence.py` es solamente un stub para una
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

OCR es opcional para layouts sin campos OCR. La demo principal configura docTR
junto con `MnistDigitIcrEngine`; antes de ejecutarla se debe preparar el modelo
ICR con `python training/train_mnist_digit.py` e instalar el extra `ocr`. El
primer uso de docTR puede descargar pesos al caché configurado.

## Contrato de extracción

Los motores OCR e ICR reciben únicamente el ROI mediante `extract(roi)`. No
existen motores simulados ni valores prefabricados en los layouts. El pipeline
y la CLI del Core no tienen fallback: los campos OCR/ICR requieren motores
reales configurados. Los resultados reales de la demo todavía no se utilizan
para medir OCR/ICR; esa evaluación completa pertenece al Hito 3.4.

## Separación de responsabilidades

La generación sintética puede usar MNIST como fuente visual de dígitos, pero eso
no equivale a entrenar el modelo ICR. El entrenamiento ICR y la configuración
OCR son recorridos avanzados opcionales; un layout QR/OMR puede procesarse con
dependencias base, mientras que un layout con OCR/ICR requiere sus motores.
