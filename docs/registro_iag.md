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

### Entrada 8 — 2026-11-07 — Claude Code
- **Prompt (resumido):** eliminar duplicados antes de la partición (mostrando su clase y el desbalance resultante), dejarlo en una función reutilizable en `src/datos.py` y crear el notebook de exploración por secciones (qué/por qué → código → preguntas de exposición con respuesta).
- **Respuesta / qué entregó:** `src/datos.py` (`cargar_datos`, `eliminar_duplicados`, `resumen_clases`) y `notebooks/01_exploracion.ipynb` con secciones: carga y tipos, nulos y duplicados (con celda de decisión justificada), desbalance y accuracy de "nunca fraude", `Amount` y `Time` por clase (escala log y densidad), correlación de V1–V28 con `Class`, y conclusiones. Las interpretaciones de los gráficos y las conclusiones quedaron como TODO para Daniel.
- **Justificación del uso:** apoyo técnico y explicación para preparar las preguntas individuales.
- **Verificación hecha por el equipo:** _(completar: Daniel ejecuta el notebook y comprueba 1.081 duplicados = 1.062 legítimas + 19 fraudes; 283.726 filas y 473 fraudes después)_
- **Análisis crítico:** la decisión de eliminar duplicados fue del equipo; la IA la implementó. Supuesto a revisar: tratar las copias como errores de registro y no como transacciones reales repetidas. Verificar la afirmación de que la correlación de Pearson con una clase muy desbalanceada queda acotada.
- **Qué modificó o decidió el equipo:** _(completar)_

### Entrada 9 — 2026-11-07 — Claude Code
- **Prompt (resumido):** crear `02_baseline.ipynb` (formato qué/por qué → código → preguntas): partición estratificada 70/15/15 en `src/datos.py`, funciones de métricas y curva PR en `src/evaluacion.py`, Dummy `most_frequent` y regresión logística sin balanceo con `StandardScaler` en pipeline, evaluación solo en validación, tabla CSV, figuras y tiempo de entrenamiento; interpretación como TODO.
- **Respuesta / qué entregó:** `particionar()` y `tabla_particion()`; `evaluar()` (AUPRC, precisión, recall, F1, accuracy, matriz), `graficar_curva_pr()` con la línea del azar = proporción de fraudes y `graficar_matriz_confusion()`; notebook con explicación de la partición en dos pasos, de por qué la AUPRC aleatoria = prevalencia (comprobado empíricamente con puntajes al azar), de los hiperparámetros (lbfgs, C=1,0, max_iter=1000) y del escalado dentro del pipeline.
- **Justificación del uso:** apoyo técnico y explicación de conceptos no vistos en clases (regresión logística, AUPRC).
- **Verificación hecha por el equipo:** _(completar: ejecutar el notebook; comprobar que la partición suma 283.726 filas y 473 fraudes, que el % de fraude es ≈ igual en los tres conjuntos y que el ejemplo pequeño de `evaluar()` da los valores calculados a mano)_
- **Análisis crítico:** _(completar)_. Puntos a revisar: la explicación de AUPRC vs ROC-AUC (contrastar con la documentación de scikit-learn), y que lbfgs sea determinista (por eso no se fijó `random_state`).
- **Qué modificó o decidió el equipo:** _(completar)_
