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

Requiere Python 3.10 o superior (probado con 3.14.7 en Windows).

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
| Baseline (análisis) | `notebooks/02_baseline.ipynb` |
| Entrenar y guardar el modelo para la interfaz | `python -m src.entrenar_baseline` |
| Regenerar el CSV de ejemplo de la demo | `python -m src.crear_csv_ejemplo` |
| Modelos principales (Avance 2) | `notebooks/03_modelos.ipynb` |
| Interfaz | `streamlit run app/app.py` |

Los notebooks se abren con `jupyter notebook`.

### Entrenar el modelo

```bash
python -m src.entrenar_baseline
```

Entrena la regresión logística sin balanceo (baseline) con la partición 70/15/15 y genera:
- `models/logistica_sin_balanceo.joblib`: el pipeline entrenado (no se versiona; se regenera con este comando).
- `models/logistica_sin_balanceo.json`: metadatos (columnas esperadas, fecha, hiperparámetros, métricas en validación).

### Ejecutar la interfaz

```bash
streamlit run app/app.py
```

Se abre en el navegador (http://localhost:8501). Antes hay que haber entrenado el modelo. Para probarla se
puede subir cualquier CSV con las columnas `Time`, `V1`–`V28` y `Amount` (si trae `Class`, se calculan
métricas) o marcar la opción del CSV de ejemplo, `data/ejemplo_transacciones.csv`. Ese archivo tiene 2.000
transacciones del conjunto de **validación**, con sus 71 fraudes. Como su proporción de fraudes (3,55 %) es
mucho mayor que la real, la precisión que se ve en la demo es más alta que la que tendría el modelo en un banco.

## Estructura

```
├── data/          # creditcard.csv (no versionado) y ejemplo_transacciones.csv (demo)
├── notebooks/     # exploración, baseline y modelos
├── src/
│   ├── config.py           # semilla (RANDOM_STATE = 42), rutas y proporciones 70/15/15
│   ├── descargar_datos.py  # descarga del dataset con kagglehub
│   ├── datos.py            # carga sin duplicados y partición 70/15/15
│   ├── modelos.py          # definición de los pipelines
│   ├── evaluacion.py       # métricas, curva PR y matriz de confusión
│   ├── entrenar_baseline.py
│   └── crear_csv_ejemplo.py
├── models/        # modelos .joblib (no versionados) y sus metadatos .json
├── app/           # interfaz Streamlit
├── docs/          # registro IAG, diagrama de flujo, capturas
└── informe/
```

## Reproducibilidad

- Semilla única `RANDOM_STATE = 42` definida en `src/config.py`.
- Partición estratificada 70/15/15 (train/val/test); el conjunto de prueba se usa una sola vez al final.
- SMOTE y escalado se aplican dentro de un `Pipeline`, ajustados solo con entrenamiento.
