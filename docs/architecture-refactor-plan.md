# Plan de refactorización arquitectónica de FormVision

**Estado:** Aprobado para ejecución incremental  
**Rama de trabajo:** `main`  
**Estrategia:** cambios pequeños, verificables, con commit y push por etapa  
**Modelo previsto para la implementación:** Codex Terra Medium

---

## 1. Propósito

Este documento define el plan para reorganizar FormVision alrededor de fronteras arquitectónicas claras, sin cambiar innecesariamente su comportamiento.

El objetivo principal es que el paquete `formvision/` contenga únicamente el motor reutilizable de procesamiento de formularios:

```text
cargar imagen
→ alinear
→ preprocesar
→ cargar layout
→ recortar campos
→ extraer
→ validar
→ exportar
```

Las responsabilidades auxiliares deben permanecer fuera del paquete principal:

```text
formvision/   motor de procesamiento
demo/         ejecución, evaluación y presentación de la demostración
synthetic/    generación de datos y formularios sintéticos
training/     preparación y evaluación de modelos
tools/        creación e inspección de layouts
docs/         explicación del sistema y sus recorridos
```

---

## 2. Regla arquitectónica principal

Un archivo pertenece a `formvision/` únicamente cuando es necesario para procesar un formulario arbitrario que ya existe.

| Responsabilidad | Ubicación objetivo |
|---|---|
| Cargar imágenes | `formvision/` |
| Alinear páginas | `formvision/` |
| Preprocesar imágenes | `formvision/` |
| Cargar layouts | `formvision/` |
| Convertir coordenadas y recortar ROIs | `formvision/` |
| Ejecutar QR, OMR, OCR e ICR reales | `formvision/` |
| Validar resultados | `formvision/` |
| Exportar resultados | `formvision/` |
| Crear plantillas sintéticas | `synthetic/` |
| Crear formularios clean | `synthetic/` |
| Crear variantes scanned | `synthetic/` |
| Crear ground truth | `synthetic/` |
| Ejecutar y evaluar la demostración | `demo/` |
| Comparar resultados con ground truth | `demo/` |
| Generar reportes y artefactos visuales | `demo/` |
| Entrenar o preparar modelos | `training/` |
| Evaluar motores durante su desarrollo | `training/` |
| Crear y editar coordenadas | `tools/` |
| Inspeccionar visualmente layouts | `tools/` |

La dependencia permitida debe seguir esta dirección:

```text
demo ─────────┐
synthetic ────┼──► formvision
training ─────┤
tools ────────┘
```

El paquete `formvision/` no debe importar código desde `demo/`, `synthetic/`, `training/` ni `tools/`.

---

## 3. Arquitectura objetivo

```text
FormVision/
│
├── formvision/                     # Motor reutilizable
│   ├── config/
│   ├── image_processing/
│   ├── layout/
│   ├── extractors/
│   ├── validators/
│   ├── exporters/
│   └── pipeline/
│
├── demo/                           # Assets y evaluación de la demo
│   └── omr_admission/
│       ├── template/
│       ├── images/
│       │   ├── clean/
│       │   └── scanned/
│       ├── ground_truth/
│       └── evaluación/orquestación
│
├── synthetic/                      # Generación de assets ficticios
│
├── training/                       # Desarrollo y evaluación de modelos
│
├── tools/                          # Creación e inspección de layouts
│
├── scripts/                        # Entrypoints pequeños de preparación
│
├── tests/
├── docs/
└── demo.py                         # Entrada sencilla de la demostración
```

Los nombres internos definitivos podrán ajustarse durante cada hito, pero las fronteras anteriores no deben modificarse sin actualizar primero este documento.

---

## 4. Principios de ejecución

Cada etapa debe seguir el mismo ciclo:

1. Definir un alcance pequeño y cerrado.
2. Dar a Codex una instrucción explícita.
3. Revisar el diff antes de aceptar cambios.
4. Ejecutar pruebas automáticas.
5. Ejecutar manualmente el flujo afectado.
6. Confirmar que no se introdujeron cambios fuera del alcance.
7. Crear un commit enfocado.
8. Hacer push a `main`.
9. Continuar recién con la siguiente etapa.

No se deben combinar en un mismo commit:

- movimientos masivos de archivos;
- cambios de comportamiento;
- mejoras visuales;
- reescritura extensa de documentación;
- cambios de modelos o algoritmos.

Cuando sea posible, los movimientos deben realizarse con `git mv` para conservar la trazabilidad.

---

# Paso 0 — Congelar el comportamiento actual

## Objetivo

Crear una línea base confiable antes de comenzar la reorganización física.

## Alcance

- Ejecutar toda la suite actual.
- Ejecutar `python demo.py`.
- Revisar la cobertura existente del flujo principal.
- Añadir únicamente las pruebas necesarias para proteger:
  - carga del layout;
  - alineamiento;
  - recorte de ROIs;
  - selección de extractores;
  - validación;
  - resultado final;
  - evaluación completa del lote.
- No mover archivos.
- No cambiar algoritmos.
- No cambiar todavía la arquitectura.
- No mejorar la interfaz ni la documentación general.

## Validación mínima

```bash
pytest
python -m compileall formvision
python demo.py
```

También debe revisarse que `git diff --check` no reporte errores.

## Criterio de cierre

El comportamiento actual queda cubierto suficientemente para detectar regresiones durante los movimientos posteriores.

## Commit sugerido

```text
test: lock current behavior before architecture refactor
```

---

# Hito 2 — Aislamiento del núcleo `formvision`

## Objetivo

Conseguir que `formvision/` contenga exclusivamente el motor de procesamiento.

## Hito 2.1 — Delimitar el layout de runtime

El área de layout dentro de `formvision/` debe conservar únicamente lo necesario para interpretar una plantilla y recortar campos, por ejemplo:

```text
formvision/layout/
├── __init__.py
├── template_loader.py
├── coordinate_mapper.py
└── modelos o contratos del layout
```

El alcance debe limitarse a organización e imports. No se deben modificar los algoritmos de recorte o escalado.

### Commit sugerido

```text
refactor: isolate runtime layout components
```

## Hito 2.2 — Retirar generación sintética del Core

Mover fuera de `formvision/`, sin rediseñar todavía su lógica, los componentes que únicamente fabrican datos o formularios, entre ellos:

```text
synthetic_templates.py
form_overlay.py
digit_strip.py
mnist_digits.py
mnist_exporter.py
scan_simulator.py
```

La ubicación provisional o definitiva será `synthetic/`.

Se actualizarán solamente:

- imports;
- scripts consumidores;
- pruebas afectadas;
- referencias técnicas imprescindibles.

### Commit sugerido

```text
refactor: move synthetic generation outside core
```

## Hito 2.3 — Mantener únicamente extractores reales

El Core debe contener las implementaciones reales necesarias para procesar:

```text
BarcodeExtractor
OmrExtractor
DoctrOcrEngine
MnistDigitIcrEngine
```

`DemoOcrExtractor` y `DemoIcrExtractor` no deben formar parte de la arquitectura final. La transición debe planificarse sin romper el flujo antes de conectar la demo con los motores reales.

Los mocks o fakes usados exclusivamente por pruebas deben vivir bajo `tests/` y no exponerse como extractores públicos.

### Commit sugerido

```text
refactor: prepare core for real extraction engines
```

## Hito 2.4 — Retirar evaluación específica de la demo

La comparación con archivos de referencia y la evaluación del lote no forman parte del motor. La implementación actualmente asociada a la demo debe moverse fuera de `formvision/` y quedar bajo la responsabilidad de `demo/`.

El movimiento debe conservar inicialmente el comportamiento existente.

### Commit sugerido

```text
refactor: move demo evaluation outside core
```

## Hito 2.5 — Verificar fronteras

Añadir o ajustar comprobaciones que garanticen:

```text
formvision no importa demo
formvision no importa synthetic
formvision no importa training
formvision no importa tools
```

## Validación mínima

```bash
pytest
python -m compileall formvision
python -m build
python demo.py
```

## Criterio de cierre

El paquete `formvision/` solo contiene capacidades necesarias para procesar formularios existentes.

## Commit sugerido

```text
test: enforce FormVision core boundaries
```

## Tag sugerido

```text
hito-2-core-isolation
```

---

# Hito 3 — Demo real y ground truth

## Objetivo

Convertir la demostración en una ejecución honesta de los motores reales de FormVision.

## Hito 3.1 — Adoptar `ground_truth`

Renombrar conceptualmente y físicamente:

```text
demo/omr_admission/expected/
→
demo/omr_admission/ground_truth/
```

Actualizar de forma consistente:

- rutas;
- descubrimiento de archivos;
- nombres de variables;
- scripts;
- pruebas;
- mensajes;
- documentación;
- manifest.

`expected` podrá seguir utilizándose como nombre local en una comparación, pero la carpeta y el concepto del dataset serán `ground_truth`.

### Commit sugerido

```text
refactor: rename demo expected data to ground truth
```

## Hito 3.2 — Ejecutar motores reales

La demo debe configurar el pipeline con los motores reales disponibles en `formvision/`.

No debe obtener valores de reconocimiento desde el layout ni sustituir silenciosamente un motor real por uno simulado.

Si falta una dependencia opcional, la ejecución debe mostrar un mensaje claro y accionable.

### Commit sugerido

```text
feat: run demo with real extraction engines
```

## Hito 3.3 — Eliminar valores simulados

Una vez conectados los motores reales:

- eliminar `DemoOcrExtractor`;
- eliminar `DemoIcrExtractor`;
- eliminar `demo_value` del esquema del layout;
- eliminar `demo_value` de los layouts;
- actualizar generadores y pruebas.

La regla final será:

```text
FormVision nunca inventa el resultado.
Synthetic conoce el valor porque fabrica la muestra.
Ground truth conserva el valor conocido.
Demo compara lo extraído con lo conocido.
```

### Commit sugerido

```text
refactor: remove simulated extraction values
```

## Hito 3.4 — Consolidar evaluación y reportes

La demo debe:

- procesar los formularios scanned;
- invocar únicamente a FormVision para extraer datos;
- leer `ground_truth/`;
- comparar QR, OMR, OCR e ICR;
- guardar un reporte estructurado;
- registrar fallos por formulario sin ocultarlos.

Los artefactos visuales y el reporte HTML podrán añadirse después de estabilizar la evaluación real.

### Commit sugerido

```text
feat: evaluate real demo results against ground truth
```

## Validación mínima

```bash
pytest
python demo.py
```

También debe verificarse que el layout ya no contenga valores reconocidos prefabricados.

## Tag sugerido

```text
hito-3-real-demo
```

---

# Hito 4 — Generación sintética independiente

## Objetivo

Organizar `synthetic/` como la capa que fabrica los assets de la demostración, sin contaminar el motor.

## Hito 4.1 — Definir su estructura

La estructura puede evolucionar hacia algo similar a:

```text
synthetic/
├── __init__.py
├── template_factory.py
├── form_overlay.py
├── digit_renderer.py
├── digit_strip.py
├── scan_simulator.py
└── dataset_builder.py
```

Los scripts deben quedar como entrypoints pequeños que invoquen esa lógica.

### Commit sugerido

```text
refactor: organize synthetic data generation
```

## Hito 4.2 — Centralizar la geometría

Eliminar coordenadas y constantes OMR duplicadas.

Debe existir una sola fuente de verdad para:

```text
start_x
start_y
row_gap
column_gap
option_gap
bubble_radius
```

Esa geometría debe ser utilizada por:

- el generador de la plantilla;
- el generador del layout;
- el marcado de respuestas;
- las pruebas.

### Commit sugerido

```text
refactor: centralize synthetic form geometry
```

## Hito 4.3 — Dataset reproducible

Un único recorrido debe poder producir:

```text
template/template.png
template/layout.json
images/clean/
images/scanned/
ground_truth/
manifest.json
```

Debe usar:

- semillas controladas;
- IDs consistentes;
- nombres predecibles;
- correspondencia validada entre imágenes y ground truth.

### Commit sugerido

```text
feat: build reproducible synthetic demo dataset
```

## Hito 4.4 — Prueba de ida y vuelta

Generar un dataset temporal y verificar que:

- todos los assets esperados existen;
- los IDs coinciden;
- cada scanned tiene ground truth;
- FormVision puede procesar al menos una muestra;
- la generación no depende de rutas privadas.

### Commit sugerido

```text
test: verify synthetic dataset round trip
```

## Tag sugerido

```text
hito-4-synthetic-generation
```

---

# Hito 5 — Revisión de `training/`

## Objetivo

Verificar que el desarrollo de modelos esté correctamente aislado, evitando una refactorización innecesaria si la estructura actual ya es suficiente.

## Alcance

Confirmar la separación:

```text
renderizar MNIST para generar formularios  → synthetic
entrenar o preparar un modelo              → training
cargar y ejecutar el modelo                → formvision
evaluar el motor durante su desarrollo     → training
```

También se debe definir:

- dónde escribe `training/` sus artefactos;
- qué artefactos consume `formvision/`;
- cuáles se versionan;
- cuáles se ignoran;
- cuáles dependencias son opcionales.

No se moverán archivos si no existe una ganancia arquitectónica clara.

## Commits sugeridos

```text
refactor: clarify model development boundaries
```

```text
chore: standardize model artifact workflow
```

## Tag sugerido

```text
hito-5-model-development
```

---

# Hito 6 — Herramientas de layouts

## Objetivo

Mejorar la creación e inspección de coordenadas sin mezclarla con el motor.

## Hito 6.1 — Validación funcional

El editor debe detectar, como mínimo:

- IDs duplicados;
- tipos desconocidos;
- ROIs fuera de la página;
- dimensiones inválidas;
- campos OMR sin opciones;
- JSON incompleto;
- propiedades incompatibles.

### Commit sugerido

```text
feat: validate layout definitions in editor
```

## Hito 6.2 — Mejora visual y de uso

Después de estabilizar la validación podrán evaluarse mejoras como:

- panel lateral de campos;
- color por tipo de extractor;
- zoom y desplazamiento;
- selección más clara;
- coordenadas visibles;
- duplicación de campos;
- mejor jerarquía de botones;
- mensajes de validación;
- diseño visual más cuidado.

La herramienta debe seguir siendo pequeña y comprensible.

### Commit sugerido

```text
feat: improve layout editor experience
```

## Hito 6.3 — Inspección visual

Permitir una revisión clara de:

```text
template
+ ROIs
+ IDs
+ etiquetas
+ tipos de campo
```

No es necesario ejecutar OCR o ICR desde el navegador.

### Commit sugerido

```text
feat: add layout visual inspection workflow
```

## Tag sugerido

```text
hito-6-layout-tools
```

---

# Hito 7 — Documentación y cierre

## Objetivo

Actualizar la documentación cuando las fronteras físicas ya sean reales y estables.

## Recorrido que debe explicar la documentación final

```text
1. tools crea o edita layout.json
2. synthetic crea los assets y ground truth
3. training prepara los modelos opcionales
4. formvision procesa los formularios
5. demo evalúa y presenta los resultados
```

## Estructura documental sugerida

```text
README.md
docs/
├── architecture.md
├── processing-pipeline.md
├── demo.md
├── layouts.md
├── synthetic-data.md
├── models.md
├── development.md
└── architecture-refactor-plan.md
```

## Trabajo requerido

- eliminar contradicciones históricas;
- sustituir referencias obsoletas a `expected/`;
- eliminar menciones a `demo_value`;
- documentar dependencias opcionales;
- documentar la ejecución real de `python demo.py`;
- explicar claramente las cinco fronteras;
- revisar todos los comandos;
- seleccionar y aplicar una licencia definitiva.

## Commits sugeridos

```text
docs: align documentation with final architecture
```

```text
chore: finalize public project metadata and license
```

## Tag sugerido

```text
hito-7-architecture-complete
```

---

## 5. Orden de ejecución

```text
Paso 0   Congelar el comportamiento actual
Hito 2   Aislar el núcleo formvision
Hito 3   Convertir la demo a motores reales y ground truth
Hito 4   Organizar la generación sintética
Hito 5   Revisar y delimitar training
Hito 6   Mejorar tools
Hito 7   Actualizar documentación y cerrar la arquitectura
```

La secuencia de dependencias será:

```text
Core estable
→ Demo real
→ Synthetic reproducible
→ Training delimitado
→ Tools mejorado
→ Documentación definitiva
```

---

## 6. Estado de avance

| Etapa | Estado |
|---|---|
| Plan arquitectónico | Aprobado |
| Paso 0 — Congelar comportamiento | Pendiente |
| Hito 2 — Core | Pendiente |
| Hito 3 — Demo real | Pendiente |
| Hito 4 — Synthetic | Pendiente |
| Hito 5 — Training | Pendiente |
| Hito 6 — Tools | Pendiente |
| Hito 7 — Documentación final | Pendiente |

Este cuadro debe actualizarse al cerrar cada hito.

---

## 7. Restricciones

Durante toda la refactorización:

- no utilizar ni incorporar archivos privados o de `legacy/`;
- no introducir rutas, datos, reglas ni modelos propietarios;
- no modificar algoritmos fuera del alcance del hito;
- no hacer movimientos masivos sin pruebas previas;
- no ocultar fallos de OCR, ICR, OMR o alineamiento;
- no mantener resultados simulados en el producto final;
- no crear ramas innecesarias si el trabajo se ejecuta directamente en `main`;
- no hacer commit ni push sin revisar antes el diff y las validaciones;
- no considerar cerrado un hito mientras la documentación y el código se contradigan en aspectos relevantes.

---

## 8. Definición final de éxito

La refactorización se considerará terminada cuando:

1. `formvision/` sea un motor agnóstico a la demo y a los datos sintéticos.
2. La demo use extractores reales y compare contra `ground_truth/`.
3. La generación sintética pueda reconstruir el dataset de forma reproducible.
4. `training/` prepare artefactos sin ser una dependencia del Core.
5. `tools/` permita crear y validar layouts de forma clara.
6. Las fronteras de importación estén verificadas.
7. La suite completa y `python demo.py` funcionen.
8. La documentación describa exactamente el comportamiento y la estructura reales.
