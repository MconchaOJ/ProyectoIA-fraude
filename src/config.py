"""
Configuración central del proyecto.

Todo valor que deba ser igual en notebooks, scripts y la interfaz se define aquí,
en un solo lugar, para garantizar la reproducibilidad (requisito del curso).
"""
from pathlib import Path

# --- Reproducibilidad ---
# Semilla única para particiones y modelos. Si se cambia aquí, cambia en todo el proyecto.
RANDOM_STATE = 42

# --- Rutas ---
# Se calculan relativas a este archivo para que funcionen sin importar desde dónde se ejecute.
RAIZ = Path(__file__).resolve().parent.parent
DIR_DATOS = RAIZ / "data"
DIR_MODELOS = RAIZ / "models"
DIR_CAPTURAS = RAIZ / "docs" / "capturas"
RUTA_CSV = DIR_DATOS / "creditcard.csv"

# --- Dataset ---
DATASET_KAGGLE = "mlg-ulb/creditcardfraud"
COLUMNA_OBJETIVO = "Class"  # 1 = fraude, 0 = legítima

# --- Partición estratificada 70/15/15 ---
# Se hace en dos pasos: primero se separa el 30% (val + test) y luego ese 30% se divide en mitades.
PROP_TRAIN = 0.70
PROP_VAL = 0.15
PROP_TEST = 0.15
