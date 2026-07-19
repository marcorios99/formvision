# Auditoría documental — Hito 0

Auditoría de todos los archivos `*.md` del repositorio, excluyendo `.venv/`,
`build/`, `dist/` y `*.egg-info/`. No se han eliminado ni modificado los
Markdown existentes.

## 1. Inventario de Markdown

| Ruta | Propósito actual | Contenido único que aporta | ¿Está actualizado? | ¿Contradice otro documento? | ¿Duplica información? | Recomendación | Documento de destino si se fusiona | Riesgo de eliminarlo |
|---|---|---|---|---|---|---|---|---|
| `README.md` | Entrada principal: descripción, instalación, quickstart, estructura, comandos, ejemplo de salida, limitaciones y roadmap | Único punto de entrada completo para alguien que clona el repositorio; reúne dependencias base y extras `mnist`/`ocr` | Parcialmente. Mezcla demo preparada, regeneración de assets y CLI avanzada; ya usa `template.png` | Sí, su flujo no coincide exactamente con `docs/flow.md` ni con `demo/omr_admission/README.md` | Alta con `architecture`, `flow`, `design-decisions`, `limitations` y `current-workflows` | conservar y actualizar | — | Muy alto |
| `demo/omr_admission/README.md` | Describe la estructura y el flujo local de la demo | Contexto específico de `template/`, `images/`, `expected/` y `results/` | Parcialmente. Usa `template.png` y presenta la ruta MNIST/docTR como flujo principal | Sí: repite el flujo de `README.md` y `docs/flow.md` | Alta | fusionar | `docs/workflows.md` | Medio-alto |
| `docs/architecture.md` | Explica capas del paquete, demo, scripts, training, tools y pipeline | Mapa técnico compacto y tipos de extractores QR/OMR/ICR/OCR | Parcialmente. La arquitectura es válida, pero debe alinearse con la estructura documental y de ejemplos aprobada | No directamente | Media con `README.md` y `docs/design-decisions.md` | conservar y actualizar | — | Alto |
| `docs/current-workflows.md` | Inventario amplio de comandos y recorridos A–E, dependencias y golden path | Análisis actual de duplicados, dependencias reales, puntos desconectados y ausencia de comparación/visualización de etapas | Válido como fotografía del estado actual; usa la nomenclatura antigua y es demasiado extenso para ser la documentación final | Sí, identifica contradicciones con `README.md`, `flow.md` y el README de demo | Alta | fusionar | `docs/workflows.md` y partes en `templates.md`/`models.md` | Medio |
| `docs/design-decisions.md` | Registra decisiones sobre demo sintética, carpeta `demo/`, ICR restringido y OCR opcional | Justificación histórica y técnica de synthetic-only, ICR por dígitos separados y docTR opcional | Conceptualmente sí; la decisión sobre la carpeta de demo puede cambiar | Puede quedar en tensión con `examples/` frente a `demo/`, pero no contradice el pipeline | Media con `architecture`, `README.md` y `limitations` | fusionar | `docs/architecture.md` y `docs/synthetic-data.md` | Medio |
| `docs/flow.md` | Flujo lineal corto del viewer a la generación y procesamiento | La secuencia operativa más breve de la demo existente | Parcialmente actualizado: incluye `template.png`, pero no incluye comparación con `expected` y mezcla edición con regeneración | Sí: puede sugerir editar y luego regenerar, aunque el batch sobrescribe el layout | Alta con los documentos de workflow | fusionar | `docs/workflows.md` | Medio-alto |
| `docs/limitations.md` | Limitaciones de ICR, OCR, perspectiva, datos sintéticos y futuras mejoras | Lista concentrada de límites técnicos y de alcance productivo | Parcialmente. Sigue siendo válida, pero debe dividirse entre modelos, datos y arquitectura | No directamente | Media con `README.md`, `design-decisions.md` y `current-workflows.md` | fusionar | `docs/models.md` y `docs/architecture.md` | Medio |

No hay Markdown separado para plantillas, datos sintéticos o modelos. Esa
información está distribuida entre README, documentación de flujo, decisiones,
limitaciones y el README de la demo.

## 2. Estructura documental objetivo

La estructura propuesta es adecuada:

```text
README.md
LICENSE
docs/
  workflows.md
  templates.md
  synthetic-data.md
  models.md
  architecture.md
```

`LICENSE` es un archivo raíz no Markdown y debe mantenerse allí; no necesita un
documento duplicado dentro de `docs/`.

| Documento destino | Contenido que debe concentrar |
|---|---|
| `README.md` | Qué es FormVision, instalación mínima, golden path breve, estructura resumida, enlaces a `docs/` y límites básicos. Los detalles extensos de comandos deben salir de aquí. |
| `docs/workflows.md` | Preparación de la demo, flujo principal `template.png → layout.json → scanned → procesamiento → expected → visualización`, generación avanzada, entrenamiento/evaluación y CLI avanzada. Fusiona `docs/flow.md`, el flujo de `demo/omr_admission/README.md` y el análisis de `current-workflows.md`. |
| `docs/templates.md` | Formulario base, viewer HTML, layout JSON, campos, ROIs y validadores. Toma contenido de README, demo README, `flow.md` y `current-workflows.md`. |
| `docs/synthetic-data.md` | Generación de plantilla/formularios, `build_student_batch.py`, escaneos simulados, clean/scanned/expected, MNIST como fuente y correspondencia por nombre. Toma contenido de README, `design-decisions.md` y `current-workflows.md`. |
| `docs/models.md` | Modelo pequeño ICR con MNIST, entrenamiento, evaluación por ROI, límites de segmentación y configuración de OCR docTR pretrained. Toma contenido de README, `design-decisions.md`, `limitations.md` y `current-workflows.md`. |
| `docs/architecture.md` | Capas, pipeline, extractores, validación, exporters, artefactos y decisiones estructurales. Conserva su contenido actual y absorbe las decisiones técnicas y limitaciones no específicas de modelos. |

No se recomienda mantener seis fuentes completas de flujo. Si se conserva
`demo/omr_admission/README.md`, debería quedar como ficha local corta que enlace
a `docs/workflows.md`.

## 3. Referencias migradas a `template.png`

La nomenclatura actual es `template.png`; el renombrado ya fue aplicado.

### Inventario de referencias

| Archivo actual | Referencia/uso | Categoría | Cambios necesarios | Riesgos |
|---|---|---|---|---|
| `README.md` | Guía: `demo/omr_admission/template/template.png` | Documentación | Referencia actualizada | Bajo |
| `demo/omr_admission/README.md` | Estructura `template/template.png` y paso de carga | Documentación | Referencia actualizada | Bajo |
| `docs/flow.md` | Paso 2 carga `demo/omr_admission/template/template.png` | Documentación | Referencia actualizada | Bajo |
| `docs/current-workflows.md` | Inventario, recorrido B/C, ejemplos de `inspect-layout` y análisis de rutas | Documentación | Actualizar al fusionarlo en `workflows.md`/`templates.md`; conservar la referencia solo como estado histórico si corresponde | Medio |
| `scripts/build_student_batch.py:49` | `base_form_path = template_dir / "template.png"` | Código/script | Referencia actualizada | Bajo |
| `scripts/build_digit_overlay_example.py:36` | `base_form_path = template_dir / "template.png"` | Código/script | Referencia actualizada | Bajo |
| `formvision/` | No hay referencias literales encontradas | Código | No hay cambio directo; la CLI recibe rutas o usa defaults distintos | Bajo |
| `tests/` | No hay referencias encontradas | Pruebas | No hay cambio directo; convendría añadir cobertura de resolución del asset al migrar | Bajo ahora; medio después |
| `tools/` | No hay referencias encontradas; el viewer carga archivos elegidos por el usuario | Herramienta | Solo actualizar documentación asociada | Bajo |

### Rutas generadas

Los dos scripts de overlays consumen actualmente:

```text
demo/omr_admission/template/template.png
demo/omr_admission/template/layout.json
```

`build_student_batch.py` y `build_digit_overlay_example.py` vuelven a generar la
imagen base mediante `SyntheticOmrSheetFactory`; además producen PNGs clean,
scanned o de ejemplo y archivos expected/metadata. La CLI
`generate-omr-sheet` no usa ese nombre por defecto: genera
`data/outputs/omr_sheet_001.png`. `inspect-layout` y el viewer aceptan cualquier
ruta y no dependen de un nombre fijo.

### Ruta objetivo

La estructura solicitada sería:

```text
examples/omr_admission/template/
  template.png
  layout.json
```

La alternativa de menor riesgo, sin reorganizar carpetas, es:

```text
demo/omr_admission/template/
  template.png
  layout.json
```

Actualmente todos los scripts y documentos usan `demo/omr_admission`; migrar a
`examples/` sería un cambio de estructura adicional y no solo de nomenclatura.

## 4. Flujos documentales requeridos

### Preparación de la demostración

Debe distinguir estos pasos:

1. Usar o crear `template.png` y `layout.json`.
2. Crear datos sintéticos clean y valores expected.
3. Generar escaneos simulados desde clean.
4. Crear el modelo pequeño ICR con MNIST si se desea el motor real.
5. Configurar opcionalmente el OCR pretrained de docTR.

La instalación y demo determinista deben quedar separadas de MNIST/docTR: los
modelos opcionales no son requisito universal para ejecutar la demo.

### Flujo principal

La documentación final debe presentar una sola secuencia:

```text
template.png
→ definición de campos en layout.json
→ lote de formularios scanned
→ procesamiento
→ comparación con expected
→ visualización
```

En el estado actual, la comparación con `expected` y la visualización de etapas
no están automatizadas. No hay comando que lea `expected/` para comparar ni una
vista que produzca imágenes de alineación, dropout, recortes o resultados. La
documentación debe marcar esos pasos como manuales o pendientes, no como
funcionalidad existente.

### Flujos avanzados

`docs/workflows.md` debe separar generación sintética, entrenamiento/evaluación y
CLI avanzada. Los comandos de bajo nivel (`compose-digit-strip`,
`paste-digit-strip`) deben presentarse como auxiliares, no como camino inicial.

## 5. Plan seguro para adoptar `template.png`

Este plan no se ejecutó:

1. Aprobar primero la ruta: se recomienda
   `demo/omr_admission/template/template.png`; usar `examples/` requeriría además
   aprobar la reorganización del demo.
2. Confirmar cambios locales y conservar una copia recuperable de
   `template.png`. No eliminar archivos automáticamente.
3. El cambio de nombre ya aplicado debe conservarse como rename reconocible por
   Git.
4. Actualizar las dos rutas en `scripts/` y todas las referencias documentales
   del inventario.
5. Buscar nuevamente `template.png` en todo el repositorio, no solo en Markdown,
   para confirmar que no quedan consumidores activos.
6. No ejecutar los batches sobre un layout editado sin copia: ambos regeneran la
   plantilla y `layout.json`.
7. Añadir una prueba de existencia/resolución del asset cuando el nuevo nombre
   forme parte del contrato del demo.
8. Verificar el diff antes de eliminar el nombre antiguo; no borrar el archivo
   anterior como parte automática de esta tarea.

## 6. Resumen de recomendaciones

### Conservar

- `README.md`, actualizándolo para que sea una entrada breve.
- `docs/architecture.md`, actualizándolo con la estructura final.

### Fusionar

- `demo/omr_admission/README.md` y `docs/flow.md` → `docs/workflows.md`.
- `docs/current-workflows.md` → principalmente `workflows.md`, con partes en
  `templates.md`, `synthetic-data.md` y `models.md`.
- `docs/design-decisions.md` → `architecture.md` y `synthetic-data.md`.
- `docs/limitations.md` → `models.md` y `architecture.md`.

### Eventualmente eliminables

No se recomienda eliminar ningún Markdown en el Hito 0. Después de crear y
validar los cinco documentos objetivo, podrían archivarse o eliminarse
eventualmente `docs/flow.md`, `docs/design-decisions.md`, `docs/limitations.md`,
`docs/current-workflows.md` y el README local de la demo, siempre que su
contenido ya esté fusionado y exista un historial Git recuperable. La
eliminación prematura tiene riesgo medio o alto porque cada archivo contiene
contexto que todavía no está consolidado.

## 7. Estado de Git

La auditoría se realizó en la rama `chore/project-foundation`. No se hizo commit
ni push y no se modificaron archivos existentes.

En esta copia, `git diff --stat` no incluye archivos nuevos no staged; después de
crear este documento el estado esperado es un único archivo nuevo:

```text
?? docs/documentation-audit.md
```
