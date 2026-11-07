# Registro de uso de IA generativa (Anexo IAG)

Proyecto: Detección de fraude en transacciones bancarias (Tema 12) — IA 2026-2, UBB.
Formato por entrada definido en `CLAUDE.md`, sección 8.

---

### Entrada 1 — Claude chat — Orientación inicial
- **Prompt (resumido):** orientación sobre la tarea del proyecto semestral.
- **Respuesta / qué entregó:** _(completar)_
- **Justificación del uso:** _(completar)_
- **Verificación hecha por el equipo:** _(completar)_
- **Análisis crítico:** _(completar)_
- **Qué modificó o decidió el equipo:** _(completar)_

### Entrada 2 — Claude chat — Plan por entregas
- **Prompt (resumido):** plan de trabajo por entregas.
- **Respuesta / qué entregó:** plan por hitos.
- **Justificación del uso:** planificación.
- **Verificación hecha por el equipo:** se contrastó con el enunciado.
- **Análisis crítico:** _(completar)_
- **Qué modificó o decidió el equipo:** _(completar)_

### Entrada 3 — Claude chat — Material de clases y dataset
- **Prompt (resumido):** envío de 12 PDF de clases y solicitud de recomendación de dataset.
- **Respuesta / qué entregó:** recomendó el dataset Credit Card Fraud (ULB); señaló que regresión logística, Random Forest, Isolation Forest, SMOTE y AUPRC no se han visto en clases.
- **Justificación del uso:** _(completar)_
- **Verificación hecha por el equipo:** _(completar)_
- **Análisis crítico:** _(completar)_
- **Qué modificó o decidió el equipo:** _(completar)_

### Entrada 4 — Claude chat — Borrador de la propuesta
- **Prompt (resumido):** redacción de un borrador de la propuesta.
- **Respuesta / qué entregó:** borrador.
- **Justificación del uso:** apoyo en redacción.
- **Verificación hecha por el equipo:** revisado y ajustado por el equipo.
- **Análisis crítico:** _(completar)_
- **Qué modificó o decidió el equipo:** _(completar)_

### Entrada 5 — 2026-11-07 — Claude chat
- **Prompt (resumido):** revisión del enunciado y la propuesta; checklist del Avance 1; generación de `CLAUDE.md`.
- **Respuesta / qué entregó:** checklist y archivo `CLAUDE.md`.
- **Justificación del uso:** planificación y contexto para Claude Code.
- **Verificación hecha por el equipo:** _(completar)_
- **Análisis crítico:** _(completar)_
- **Qué modificó o decidió el equipo:** _(completar)_

### Entrada 6 — 2026-11-07 — Claude Code
- **Prompt (resumido):** leer `CLAUDE.md` y crear lo necesario para empezar el proyecto.
- **Respuesta / qué entregó:** estructura de carpetas, `git init`, `.gitignore`, `src/config.py` (semilla 42, rutas, proporciones 70/15/15), `src/descargar_datos.py` (descarga con kagglehub), `requirements.txt` sin versiones fijadas, este registro y `docs/progreso.md`.
- **Justificación del uso:** apoyo técnico para preparar la estructura base y la reproducibilidad.
- **Verificación hecha por el equipo:** _(completar: p. ej., ejecutar `python -m src.descargar_datos` y comprobar 284.807 filas / 492 fraudes)_
- **Análisis crítico:** _(completar)_
- **Qué modificó o decidió el equipo:** se usa `ProyectoIA` como raíz del repo; la instalación del entorno queda para después.

### Entrada 7 — 2026-11-07 — Claude Code
- **Prompt (resumido):** continuar con la preparación: entorno, descarga de datos y README.
- **Respuesta / qué entregó:** fijó versiones en `requirements.txt`, ejecutó `src/descargar_datos.py` y verificó el CSV (284.807 filas, 492 fraudes, 0 nulos, 1.081 duplicados); redactó `README.md` con instalación desde cero, fuente, licencia y cita del dataset.
- **Justificación del uso:** apoyo técnico en reproducibilidad y documentación.
- **Verificación hecha por el equipo:** _(completar: repetir la instalación en otro equipo siguiendo el README)_
- **Análisis crítico:** los conteos salen de ejecutar código, no de la IA. Revisar que la cita de Dal Pozzolo et al. (2015) coincida con la indicada en la página de Kaggle.
- **Qué modificó o decidió el equipo:** _(completar; pendiente decidir el tratamiento de duplicados)_
