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

| Paso | Comando / archivo |
|---|---|
| Exploración de datos | `notebooks/01_exploracion.ipynb` |
| Baseline | `notebooks/02_baseline.ipynb` |
| Modelos principales | `notebooks/03_modelos.ipynb` |
| Interfaz | `streamlit run app/app.py` |

Los notebooks se abren con `jupyter notebook` desde la raíz del proyecto (con el entorno activado).

## Estructura

```
├── data/          # creditcard.csv (no versionado)
├── notebooks/     # exploración, baseline y modelos
├── src/
│   ├── config.py           # semilla (RANDOM_STATE = 42), rutas y proporciones 70/15/15
│   └── descargar_datos.py  # descarga del dataset con kagglehub
├── models/        # modelo final .joblib (no versionado)
├── app/           # interfaz Streamlit
├── docs/          # registro IAG, diagrama de flujo, capturas
└── informe/
```

## Reproducibilidad

- Semilla única `RANDOM_STATE = 42` definida en `src/config.py`.
- Partición estratificada 70/15/15 (train/val/test); el conjunto de prueba se usa una sola vez al final.
- SMOTE y escalado se aplican dentro de un `Pipeline`, ajustados solo con entrenamiento.
