# Detección de fraude en transacciones bancarias (Tema 12)

Proyecto semestral de Inteligencia Artificial 2026-2 — Ingeniería Civil en Informática, Universidad del Bío-Bío.
Equipo: Daniel Canto, Diego Figueroa, Maximiliano Concha. Docente: Danelys Brito González.

Sistema de aprendizaje automático que asigna un **puntaje de riesgo de fraude** a cada transacción y permite
elegir el **umbral de decisión** desde una interfaz en Streamlit. Métrica principal: **AUPRC** (la accuracy
engaña porque solo el 0,172 % de las transacciones son fraude).

> **Aviso ético:** los resultados son académicos y no constituyen una decisión sobre clientes reales.

## Datos

- **Credit Card Fraud Detection** — Machine Learning Group, ULB. Kaggle: <https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud>
- 284.807 transacciones, 492 fraudes. Columnas: `Time`, `V1`–`V28` (componentes PCA anonimizados), `Amount`, `Class` (1 = fraude).
- Licencia: Open Database License (ODbL).
- Cita: Dal Pozzolo, A., Caelen, O., Johnson, R. A. y Bontempi, G. (2015). *Calibrating Probability with Undersampling for Unbalanced Classification*. IEEE SSCI.
- El CSV **no se versiona** (pesa ~150 MB); se descarga con el script indicado abajo.

## Instalación desde cero

Requiere **Python 3.14** (probado con **Python 3.14.6** en Windows; versiones anteriores como Python 3.10 producen errores de compatibilidad con las dependencias fijadas en `requirements.txt`).

```bash
# 1. Crear y activar el entorno virtual
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# 2. Instalar dependencias (versiones fijadas)
pip install -r requirements.txt

# 3. Descargar el dataset a data/creditcard.csv (desde la raíz del proyecto)
python -m src.descargar_datos
```

Si la descarga falla por credenciales de Kaggle, bajar el ZIP manualmente desde la página del dataset y
dejar `creditcard.csv` dentro de `data/`.

## Ejecución

Todos los comandos se ejecutan desde la raíz del proyecto, con el entorno activado.

| Paso | Comando / archivo |
|---|---|
| Exploración de datos | `notebooks/01_exploracion.ipynb` |
| Baseline lineal | `notebooks/02_baseline.ipynb` |
| Modelado comparativo (Avance 2) | `notebooks/03_modelos.ipynb` |
| Entrenar todos los modelos (Avance 2) | `python -m src.entrenar_modelos` |
| Entrenar solo baseline | `python -m src.entrenar_baseline` |
| Regenerar CSV de ejemplo | `python -m src.crear_csv_ejemplo` |
| Interfaz en Streamlit | `streamlit run app/app.py` |

Los notebooks se abren con `jupyter notebook`.

### Entrenar los modelos

```bash
# Entrena los 5 modelos del Avance 2 (Random Forest, SMOTE, Balanced, Baseline, Isolation Forest)
python -m src.entrenar_modelos
```

Genera los binarios serializados `.joblib` y sus metadatos `.json` en `models/`, además de la comparativa de validación en `docs/resultados_modelos_val.csv`.

### Ejecutar la interfaz

```bash
streamlit run app/app.py
```

- **Video demostración Streamlit:** [https://youtu.be/-i5SbHytWRg](https://youtu.be/-i5SbHytWRg)

Se abre en el navegador (http://localhost:8501). Si acabas de clonar el repositorio, la app funciona de inmediato con el modelo baseline incluido (`models/logistica_sin_balanceo.joblib`); para habilitar los 5 modelos del Avance 2 en local, ejecuta primero `python -m src.entrenar_modelos`. Para probarla se
puede subir cualquier CSV con las columnas `Time`, `V1`–`V28` y `Amount` (si trae `Class`, se calculan
métricas) o marcar la opción del CSV de ejemplo, `data/ejemplo_transacciones.csv`. Ese archivo tiene 2.000
transacciones del conjunto de **validación**, con sus 71 fraudes. Como su proporción de fraudes (3,55 %) es
mucho mayor que la real, la precisión que se ve en la demo es más alta que la que tendría el modelo en un banco.

## Estructura

```
├── data/          # creditcard.csv (no versionado) y ejemplo_transacciones.csv (demo)
├── notebooks/     # exploración (01), baseline (02) y modelado comparativo (03)
├── src/
│   ├── config.py           # semilla (RANDOM_STATE = 42), rutas y proporciones 70/15/15
│   ├── descargar_datos.py  # descarga del dataset con kagglehub
│   ├── datos.py            # carga sin duplicados y partición 70/15/15
│   ├── modelos.py          # definición de los pipelines (Baseline, Pesos, SMOTE, RF, IF)
│   ├── evaluacion.py       # métricas, curva PR y matriz de confusión
│   ├── entrenar_baseline.py
│   ├── entrenar_modelos.py # entrenamiento y comparativa completa del Avance 2
│   └── crear_csv_ejemplo.py
├── models/        # metadatos .json, baseline .joblib y binarios entrenados localmente
├── app/           # interfaz Streamlit multi-modelo
├── docs/          # registro IAG, presentaciones, métricas de validación y capturas
└── informe/       # informes técnicos en PDF (Avance 1 y Avance 2)
```

## Reproducibilidad

- Semilla única `RANDOM_STATE = 42` definida en `src/config.py`.
- Partición estratificada 70/15/15 (train/val/test); el conjunto de prueba se usa una sola vez al final.
- El escalado y el sobremuestreo (SMOTE) se aplican dentro de un `Pipeline`, ajustados solo con entrenamiento para evitar fuga de información (*data leakage*).

## Estado de Avances

- **Avance 1:**
  - Auditoría exploratoria y eliminación de 1.081 duplicados (`notebooks/01_exploracion.ipynb`).
  - Partición estratificada y evaluación del baseline con AUPRC 0,688 (`notebooks/02_baseline.ipynb`).
  - Pipeline de inferencia y serialización del modelo (`src/entrenar_baseline.py`).
  - Prototipo funcional de la interfaz en Streamlit (`app/app.py`).
  - Informe formal en PDF (`informe/`) y Anexo IAG completado (`docs/registro_iag.md`).

- **Avance 2:**
  - Implementación de `class_weight='balanced'`, SMOTE solo en entrenamiento (`imblearn.Pipeline`), Random Forest (`max_depth=12`) e Isolation Forest (`IsolationForestWrapper`) en `src/modelos.py`, `src/entrenar_modelos.py` y `notebooks/03_modelos.ipynb`.
  - Comparativa en validación contra el baseline: Random Forest alcanza AUPRC `0,828` (vs `0,688` del baseline).
  - Interfaz Streamlit actualizada con selector multi-modelo, caché de doble nivel y comparativa poblacional (`app/app.py`).
  - **Video demostración Streamlit:** [https://youtu.be/-i5SbHytWRg](https://youtu.be/-i5SbHytWRg)
  - Informe técnico (`informe/Avance2_Deteccion_Fraude_UBB.pdf`), presentaciones en PDF (`docs/`) y Anexo IAG actualizado (`docs/registro_iag.md`).
