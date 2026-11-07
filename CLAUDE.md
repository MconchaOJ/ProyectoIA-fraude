# CLAUDE.md — Proyecto Semestral IA 2026-2: Detección de fraude en transacciones bancarias (Tema 12)

Este archivo le da contexto a Claude Code sobre el proyecto. Léelo completo antes de empezar.
Idioma de trabajo: **español** (código con nombres en español o inglés, pero comentarios y documentación en español).

---

## 1. Contexto académico

- **Asignatura:** Inteligencia Artificial — Ingeniería Civil en Informática, Universidad del Bío-Bío (DCCTI-UBB), Chillán.
- **Docente:** Danelys Brito González.
- **Equipo:**
  | Integrante | Responsabilidad principal |
  |---|---|
  | Daniel Canto | Datos, análisis exploratorio y baseline |
  | Diego Figueroa | Modelos, manejo del desbalance y métricas |
  | Maximiliano Concha | Interfaz en Streamlit e integración |
- **Tema asignado:** Nº 12, Área 3 (Aprendizaje Automático): *Detección de fraude en transacciones bancarias*.

### Reglas del curso que condicionan cómo trabajas (IMPORTANTE)

1. **Prohibido usar IA para generar el proyecto completo.** El enunciado dice: *"No se pueden usar modelos, ni APIs de IA para encontrar soluciones óptimas ni resultados, deben desarrollar el proyecto ustedes"* y *"No se permite el uso de IAG para generar código completo sin análisis propio."* Los reportes pasan por revisión de originalidad y trazabilidad.
2. **Preguntas técnicas individuales** en cada avance: cualquier integrante puede ser interrogado sobre cualquier parte del código, decisiones, hiperparámetros y resultados.
3. **Anexo IAG obligatorio (15% de la nota):** registrar prompts, respuestas, justificación del uso, análisis crítico (¿preciso, sesgado, alucinado?), reflexión ética y autoevaluación.

**Por lo tanto, Claude Code debe:**
- Trabajar **por partes pequeñas**, no generar el proyecto entero de una vez.
- **Explicar cada decisión** (qué hace el código, por qué esa técnica o ese parámetro, qué alternativas había), para que el equipo pueda defenderlo oralmente.
- Preferir **esqueletos con TODOs y guía** cuando el equipo lo pida, para que ellos completen y ejecuten.
- Revisar, depurar y comentar el código que escriba el equipo.
- Al terminar cada sesión de trabajo relevante, **agregar una entrada en `docs/registro_iag.md`** (ver sección 8).
- Nunca inventar resultados ni métricas: los números salen de ejecutar el código.

---

## 2. El problema (de la propuesta entregada el 29/10)

El fraude con tarjetas es muy poco frecuente: en el dataset, 492 de 284.807 transacciones (0,172%) son fraude. Un clasificador que nunca alerta acierta el 99,83% y no detecta ningún fraude, por eso **la accuracy no sirve como métrica**. Un falso negativo es dinero perdido; un falso positivo es un cliente con su pago bloqueado. El sistema asigna un **puntaje de riesgo** a cada transacción y permite **elegir el umbral de decisión** según ese equilibrio.

### Objetivos
- **General:** desarrollar y evaluar un sistema de ML que asigne un puntaje de riesgo de fraude a transacciones con alto desbalance de clases, con una interfaz que permita ajustar el umbral de decisión.
- **OE1:** entrenar y comparar regresión logística, Random Forest e Isolation Forest con dos estrategias de desbalance (`class_weight` y SMOTE solo en entrenamiento), sobre partición estratificada 70/15/15 con semilla fija, y superar al baseline en **AUPRC** en el conjunto de prueba, informando también precisión y recall.
- **OE2:** interfaz en Streamlit conectada al mejor modelo: cargar un CSV, ver el puntaje de riesgo de cada transacción y mover el umbral, mostrando en tiempo real falsos positivos, falsos negativos, precisión y recall.

### Modelos
| Rol | Modelo | Motivo |
|---|---|---|
| Baseline 1 | `DummyClassifier` «nunca fraude» | Muestra por qué la accuracy engaña (≈99,83%, recall 0) |
| Baseline 2 | Regresión logística sin manejo del desbalance | Referencia lineal e interpretable |
| Principal | Regresión logística y Random Forest, cada uno con `class_weight` y con SMOTE | Comparar estrategias de desbalance; RF captura no linealidades |
| No supervisado | Isolation Forest | Detecta anomalías sin etiquetas |
| Complementario | Naive Bayes gaussiano | Conecta con Teorema de Bayes (clases 9 y 10) |

**Métricas:** AUPRC (principal, `average_precision_score`), precisión, recall, matriz de confusión, curva PR. Accuracy solo para mostrar que engaña.

**Justificación con Bayes (usada en la propuesta):** con recall 90% y 1% de falsas alarmas, P(fraude | alerta) ≈ 0,9·0,00172 / (0,9·0,00172 + 0,01·0,99828) ≈ 13%.

**Enfoque de agente (PEAS):** percibe transacciones, actúa aprobando o alertando, se mide por el costo de sus errores; entorno parcialmente observable y estocástico.

**Declaración ética obligatoria (temas financieros):** los resultados son académicos y no constituyen una decisión sobre clientes reales.

---

## 3. Datos

- **Dataset:** Credit Card Fraud Detection (Machine Learning Group, ULB), Kaggle: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
- Archivo `creditcard.csv` (~150 MB): 284.807 filas, 492 fraudes. Columnas: `Time`, `V1`–`V28` (componentes PCA anonimizados), `Amount`, `Class` (1 = fraude).
- Licencia: Open Database License (ODbL). Cita: Dal Pozzolo et al. (2015).
- Limitación: V1–V28 no son interpretables.
- **No subir el CSV al repositorio** (pesa mucho): agregarlo a `.gitignore` e incluir un script de descarga (`src/descargar_datos.py`, p. ej. con `kagglehub`) e instrucciones en el README.

---

## 4. Decisiones técnicas obligatorias (no negociables)

- **Semilla fija** en todo: `RANDOM_STATE = 42` (definida en un solo lugar, `src/config.py`).
- **Partición estratificada 70/15/15** (train/val/test) con `stratify=y`.
- **SMOTE solo en entrenamiento:** usar `imblearn.pipeline.Pipeline` para que el sobremuestreo nunca toque validación ni prueba (tampoco dentro de la validación cruzada).
- **Escalado** (`StandardScaler`, sobre todo para `Amount` y `Time`) dentro del pipeline, ajustado solo con train.
- **Selección de hiperparámetros y umbral con validación**; el conjunto de **prueba se usa una sola vez**, al final, para reportar.
- **Isolation Forest:** usar `-decision_function` / `-score_samples` como puntaje de riesgo para calcular AUPRC.
- Comparar **al menos dos configuraciones** de hiperparámetros o técnicas (requisito del curso).
- Resultados en **tabla comparativa** contra el baseline.
- Guardar el modelo final con `joblib` para que lo cargue la interfaz.

---

## 5. Requisitos técnicos mínimos del curso (todos los temas)

- Código propio en Python, comentado (notebooks de Colab o scripts).
- Reproducibilidad: semillas fijas, `README.md`, `requirements.txt`, datos o script de descarga, instrucciones para ejecutar desde cero.
- Comparación con al menos un baseline, métricas en tabla.
- Partición train/val/test y comparación de al menos dos configuraciones.
- Interfaz gráfica funcional (Streamlit) conectada al modelo entrenado.
- Citar fuente y licencia de los datos.
- **Formato de entrega que pidió la profesora:** el notebook `.ipynb` **ejecutado, con todas las salidas visibles** (no link a Colab), informe en PDF y presentación en PPT o PDF adjuntos directamente.

---

## 6. Entregas y fechas (subir a Moodle hasta las 23:59 del día anterior)

| Fecha exposición | Entrega | Plazo Moodle | Contenido |
|---|---|---|---|
| ~~29 oct~~ | Propuesta | — | **Ya entregada** |
| **Jue 19 nov** | **Avance 1** | **Mié 18 nov 23:59** | ZIP código + PDF (máx. 4 págs.), exposición 5 min, máx. 4 láminas |
| Jue 26 nov | Avance 2 | Mié 25 nov 23:59 | Video 1-2 min + informe técnico (máx. 5 págs.) + ZIP |
| Jue 3 dic | Final | Mié 2 dic 23:59 | Informe PDF (máx. 10 págs.) + PPT/video + ZIP con README, requirements, dataset |

### Avance 1 — lo que hay que tener (FOCO ACTUAL)
Objetivo: validar la estructura base del modelo y su flujo de trabajo.
- [ ] Diagrama del flujo general (entrada → procesamiento → salida). Idea: CSV → validación/preprocesamiento (escalado) → modelo → puntaje de riesgo → umbral → aprobar/alertar + métricas.
- [ ] Datos cargados y explorados: tamaño, variables, distribución de clases, distribución de `Amount` y `Time` por clase, nulos y duplicados.
- [ ] Código base en Python comentado, con evidencia de funcionamiento parcial.
- [ ] Baseline ejecutado con su métrica (Dummy + regresión logística sin balanceo: AUPRC, precisión, recall, matriz de confusión, accuracy para contrastar).
- [ ] Capturas o logs de las primeras pruebas.
- [ ] Documentación inicial del entrenamiento: hiperparámetros, partición usada, resultados preliminares.
- [ ] Primer borrador de la interfaz (estructura funcional, menú, componentes). Basta un `app.py` de Streamlit con la estructura aunque use un modelo baseline.
- [ ] Descripción del apoyo recibido de IAG.

Los modelos principales (RF, SMOTE, Isolation Forest) son del Avance 2; si alcanza, mostrar uno preliminar.

### Avance 2 (26 nov)
Modelo funcional con resultados vs baseline, interfaz parcial o completa, capturas o video, análisis crítico inicial (comparación entre técnicas/parámetros), Anexo IAG parcial.

### Final (3 dic)
Informe completo (introducción, marco teórico, metodología, resultados y análisis, conclusiones técnicas y éticas, bibliografía, Anexo IAG). Interfaz final, demo en vivo, video de respaldo. Formato del informe: **Arial 11, justificado, interlineado 1,5, espaciado entre párrafos 0**; títulos Arial 12 o 14.

---

## 7. Exposiciones de avance (5 min, se corta al cumplirse)

Estructura sugerida: problema y tema (30 s) · datos y técnica (1 min) · estado actual con evidencia (2 min) · resultados vs baseline o dificultades (1 min) · próximos pasos (30 s). Luego 1-2 preguntas individuales por integrante (qué hace una parte del código, por qué una técnica o hiperparámetro, cómo se interpreta un resultado, qué sugirió la IAG y cómo se verificó).

Pauta por avance (10 pts): tiempo y estructura (2), estado técnico según el hito (2), evidencia en vivo: código, logs, métricas o interfaz (2), registro IAG al día y analizado (2), pregunta individual (2). **Menos de 4 pts de equipo = incumplimiento** y reduce la nota global.

---

## 8. Registro IAG (mantener al día)

Archivo `docs/registro_iag.md`. Por cada interacción relevante con IA (incluyendo esta con Claude Code):

```markdown
### Entrada N — AAAA-MM-DD — Herramienta (Claude Code / Claude chat)
- **Prompt (resumido):**
- **Respuesta / qué entregó:**
- **Justificación del uso:** (apoyo técnico, explicación, depuración, documentación, visualización)
- **Verificación hecha por el equipo:** (cómo se comprobó: ejecución, documentación oficial, material del curso)
- **Análisis crítico:** (¿precisa, sesgada, alucinada? errores detectados)
- **Qué modificó o decidió el equipo:**
```

Entradas previas (de la propuesta, con Claude chat): (1) orientación inicial sobre la tarea; (2) plan por entregas, verificado contra el enunciado; (3) envío de 12 PDF de clases y recomendación de dataset; detectó que regresión logística, RF, Isolation Forest, SMOTE y AUPRC no se han visto en clases; (4) borrador de la propuesta, revisado y ajustado por el equipo. (5) 07-11-2026: revisión del enunciado y la propuesta, checklist del Avance 1 y generación de este CLAUDE.md.

---

## 9. Material del curso (para alinear el marco teórico)

Clases vistas: agentes y PEAS (clase 2, cap. 2 Russell & Norvig), búsqueda no informada (BFS/DFS) e informada (GBFS, A*), lógica proposicional y sistemas basados en reglas, CommonKADS, **incertidumbre y Teorema de Bayes (clases 9 y 10)**, **RNA: perceptrón y MLP con scikit-learn (`MLPClassifier`) y Keras**, algoritmos evolutivos y genéticos (clase 11). La clase de RNA usa scikit-learn y menciona regresión logística, SVM, árboles y Random Forest como parte de la librería. Regresión logística, Random Forest, Isolation Forest, SMOTE y AUPRC **no se han visto en detalle**: el equipo debe estudiarlos, así que explícalos con claridad cuando aparezcan.

Posible extra para el marco teórico/comparación: un `MLPClassifier` conecta con la clase de RNA (opcional, no comprometido en la propuesta).

---

## 10. Estructura sugerida del repositorio

```
fraude-tema12/
├── CLAUDE.md
├── README.md               # cómo instalar, descargar datos y ejecutar todo desde cero
├── requirements.txt        # versiones fijadas
├── .gitignore              # data/*.csv, modelos pesados, __pycache__, .venv
├── data/                   # creditcard.csv (no versionado)
├── notebooks/
│   ├── 01_exploracion.ipynb
│   ├── 02_baseline.ipynb
│   └── 03_modelos.ipynb
├── src/
│   ├── config.py           # RANDOM_STATE, rutas, proporciones de partición
│   ├── descargar_datos.py
│   ├── datos.py            # carga y partición estratificada
│   ├── modelos.py          # definición de pipelines
│   └── evaluacion.py       # métricas, curva PR, matriz de confusión, tabla
├── models/                 # .joblib del modelo final
├── app/
│   └── app.py              # interfaz Streamlit
├── docs/
│   ├── registro_iag.md
│   ├── diagrama_flujo.(md|png)
│   └── capturas/
└── informe/
```

Stack: Python 3.10+, pandas, numpy, scikit-learn, imbalanced-learn, matplotlib/seaborn, streamlit, joblib, kagglehub. Desarrollo en local o Google Colab.

---

## 11. Interfaz prevista (boceto de la propuesta)

Streamlit con: carga de CSV · selección de modelo · slider de umbral · indicadores en tiempo real (FP, FN, precisión, recall, matriz de confusión) · tabla de transacciones ordenadas por puntaje de riesgo · aviso visible de que es un ejercicio académico. Si el CSV cargado trae la columna `Class`, calcular métricas; si no, solo mostrar puntajes y alertas.

---

## 12. Primer paso sugerido

1. Crear la estructura del repo, `requirements.txt`, `.gitignore`, `src/config.py` y `src/descargar_datos.py`.
2. `notebooks/01_exploracion.ipynb`: carga, tamaño, tipos, nulos, duplicados, distribución de `Class`, `Amount` y `Time` por clase.
3. `notebooks/02_baseline.ipynb`: partición 70/15/15 estratificada, Dummy y regresión logística sin balanceo, tabla de métricas en validación.
4. Esqueleto de `app/app.py`.
5. Diagrama de flujo y entrada en `docs/registro_iag.md`.

Explica cada paso al equipo y espera confirmación antes de avanzar al siguiente.
