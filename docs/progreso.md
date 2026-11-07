# Progreso del proyecto — Detección de fraude (Tema 12, IA 2026-2, UBB)

> Archivo para dar contexto a Claude chat. Lo mantiene Claude Code al día después de cada sesión.
> El contexto completo del proyecto (reglas, objetivos, decisiones técnicas, fechas) está en `CLAUDE.md`.

**Foco actual:** Avance 1. Plazo en Moodle: **mié 18 nov 2026, 23:59**. Exposición: jue 19 nov.

---

## Estado actual (2026-11-07)

### Hecho
- Raíz del proyecto: `C:\Users\coee1\Desktop\ProyectoIA` (se usa directamente como raíz del repo; no hay subcarpeta `fraude-tema12/`).
- `git init` hecho (aún sin commits ni remoto en GitHub).
- Carpetas creadas: `data/`, `notebooks/`, `src/`, `models/`, `app/`, `docs/capturas/`, `informe/` (las vacías llevan `.gitkeep`).
- `.gitignore`: excluye `data/*.csv`, `models/*.joblib`, `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`.
- `src/config.py`: `RANDOM_STATE = 42`, rutas (`RAIZ`, `DIR_DATOS`, `DIR_MODELOS`, `DIR_CAPTURAS`, `RUTA_CSV`), `DATASET_KAGGLE = "mlg-ulb/creditcardfraud"`, `COLUMNA_OBJETIVO = "Class"`, proporciones 0.70 / 0.15 / 0.15.
- `src/descargar_datos.py`: descarga con `kagglehub.dataset_download(...)` y copia `creditcard.csv` a `data/`. No vuelve a descargar si ya existe. Se ejecuta con `python -m src.descargar_datos` desde la raíz.
- `requirements.txt`: pandas, numpy, scikit-learn, imbalanced-learn, matplotlib, seaborn, streamlit, joblib, kagglehub, jupyter (**sin versiones fijadas todavía**).
- `docs/registro_iag.md` creado con las entradas previas.

### Decisiones tomadas
- **Duplicados eliminados antes de la partición** (evita fuga train→test). De las 1.081 copias, 1.062 son legítimas y 19 fraudes; no hay copias con etiqueta contradictoria. Dataset final: **283.726 filas, 473 fraudes (0,167 %)**. Implementado en `src/datos.py` (`cargar_datos()` lo aplica por defecto; `eliminar_duplicados()`, `resumen_clases()`).
- Módulos compartidos: `src/datos.py` (`cargar_datos`, `particionar`, `tabla_particion`) y `src/evaluacion.py` (`evaluar`, `graficar_curva_pr`, `graficar_matriz_confusion`). `src/modelos.py` (`crear_logistica_sin_balanceo`), `src/entrenar_baseline.py`, `src/crear_csv_ejemplo.py`. Puntaje de riesgo = `predict_proba[:, 1]` (Isolation Forest: `-score_samples`).
- Git lo maneja Maximiliano: Claude Code no hace commits.

### Pendiente inmediato
- [x] Entorno `.venv` (Python 3.14.7) creado y dependencias instaladas sin errores.
- [x] Versiones fijadas en `requirements.txt` (scikit-learn 1.9.1, imbalanced-learn 0.14.2, pandas 3.1.1, numpy 2.5.4, streamlit 1.67.0, etc.).
- [x] Dataset descargado (`python -m src.descargar_datos`) y verificado: 284.807 filas × 31 columnas, 492 fraudes (0,173 %), 0 nulos, **1.081 filas duplicadas** (decidir en la exploración si se eliminan).
- [x] `README.md` con instalación desde cero, fuente/licencia/cita de datos y estructura.

### Checklist Avance 1
- [~] Diagrama de flujo: `docs/diagrama_flujo.md` (Mermaid), con dos flujos (entrenamiento fuera de línea y uso en la interfaz), leyenda implementado / Avance 2 / prueba reservada, y tablas que explican cada bloque. Verificado que renderiza (Mermaid 11). **Falta:** exportar a PNG con mermaid.live y guardarlos en `docs/capturas/`.
- [~] `notebooks/01_exploracion.ipynb`: creado (8 secciones: qué/por qué → código → preguntas de exposición). Verificado que corre sin errores. **Falta:** que Daniel lo ejecute (genera las figuras en `docs/capturas/`) y escriba las interpretaciones/conclusiones marcadas TODO.
- [~] `notebooks/02_baseline.ipynb`: creado y verificado que corre (secciones qué/por qué → código → preguntas). Genera `docs/resultados_baseline_val.csv`, `docs/capturas/02_matriz_dummy_val.png`, `02_matriz_logistica_val.png`, `02_curva_pr_val.png`. **Falta:** que el equipo lo ejecute y escriba la interpretación (sección 6, TODO).
  - Resultados de la ejecución de prueba (validación, umbral 0,5): Dummy → accuracy 0,9983, recall 0, AUPRC 0,0017. Regresión logística sin balanceo → AUPRC 0,688, precisión 0,833, recall 0,493 (35 de 71 fraudes; FP 7, FN 36), accuracy 0,9990, entrenamiento ≈ 0,3 s (16 iteraciones de lbfgs).
- [ ] Capturas/logs de las primeras pruebas
- [~] Documentación del entrenamiento: partición (train 198.608 / 331 fraudes; val 42.559 / 71; test 42.559 / 71; % fraude ≈ 0,167 % en los tres) e hiperparámetros (lbfgs, C=1,0, max_iter=1000) documentados en el notebook 02. Falta pasarlo al PDF del avance.
- [x] Borrador de `app/app.py` (Streamlit), probado con `streamlit.testing.AppTest`: menú lateral (Analizar transacciones / Resultados del modelo / Acerca del proyecto), carga de CSV o CSV de ejemplo, validación de columnas (faltantes, no numéricas, nulos, Class ∉ {0,1}), selector de modelo (solo lista los .joblib que existen; diccionario `MODELOS` preparado para el Avance 2), slider de umbral con TP/FP/FN/TN/precisión/recall en vivo, matriz de confusión, tabla ordenada por puntaje y aviso ético en todas las secciones. Modelo con `st.cache_resource`, puntajes con `st.cache_data`.
  - Prueba con el CSV de ejemplo: umbral 0,5 → 35 alertas, TP 35, FP 0, FN 36, recall 0,493; umbral 0,05 → TP 54, FP 1, FN 17, recall 0,761.
- [x] Notebook 02 usa `crear_logistica_sin_balanceo()` de `src/modelos.py` (una sola definición del pipeline). Re-verificado: AUPRC 0,6877.
- [x] El `.joblib` ahora incluye los puntajes y etiquetas de la validación completa, y los metadatos incluyen `umbrales_val` (tabla para 0,9 / 0,5 / 0,3 / 0,1 / 0,05 / 0,01). En la app: "Resultados del modelo" muestra esa tabla y la curva PR; "Analizar" compara en vivo el CSV cargado con la validación completa para el mismo umbral. Ej. umbral 0,05: CSV de ejemplo FP 1 / precisión 0,982; validación completa FP 15 / precisión 0,783 (mismo TP 54 y recall 0,761).
- [x] Modelo guardado: `python -m src.entrenar_baseline` → `models/logistica_sin_balanceo.joblib` (+ `.json` con metadatos versionado). Métricas idénticas al notebook 02 (AUPRC 0,6877).
- [x] `data/ejemplo_transacciones.csv` (`python -m src.crear_csv_ejemplo`): 2.000 filas de VALIDACIÓN, 71 fraudes (3,55 %); sí se versiona (excepción en `.gitignore`). Ojo: su precisión es optimista por la mayor proporción de fraudes.
- [ ] Registro IAG al día

---

## Próximo paso sugerido
1. Equipo ejecuta y completa los TODO de `01_exploracion.ipynb` y `02_baseline.ipynb`.
2. Maximiliano: ejecutar `streamlit run app/app.py`, revisar la interfaz y tomar capturas para el avance.
3. Exportar los dos diagramas a PNG (instrucciones en `docs/diagrama_flujo.md`, sección 3).
4. PDF del Avance 1 (máx. 4 págs.) y láminas (máx. 4).

---

## Historial de sesiones con Claude Code
- **2026-11-07:** lectura de `CLAUDE.md`; estructura del repo, `.gitignore`, `config.py`, `descargar_datos.py`, `requirements.txt`, `registro_iag.md` y este archivo.
- **2026-11-07 (cont.):** entorno instalado y versiones fijadas; dataset descargado y verificado; `README.md`.
- **2026-11-07 (cont. 2):** `src/datos.py` (carga + eliminación de duplicados) y `notebooks/01_exploracion.ipynb`.
- **2026-11-07 (cont. 3):** partición en `src/datos.py`, `src/evaluacion.py` y `notebooks/02_baseline.ipynb`.
- **2026-11-07 (cont. 4):** `src/modelos.py`, `src/entrenar_baseline.py`, `src/crear_csv_ejemplo.py`, `app/app.py`, README (entrenar y ejecutar la app).
- **2026-11-07 (cont. 5):** notebook 02 importa el pipeline de `src/modelos.py`; tabla de umbrales y curva PR de validación completa en la app; `docs/diagrama_flujo.md`.
