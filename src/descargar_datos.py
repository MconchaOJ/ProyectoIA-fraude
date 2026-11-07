"""
Descarga el dataset Credit Card Fraud Detection (ULB) desde Kaggle y lo deja en data/creditcard.csv.

Uso (desde la raíz del proyecto):
    python -m src.descargar_datos

Fuente: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
Licencia: Open Database License (ODbL). Cita: Dal Pozzolo et al. (2015).

Si la descarga falla por credenciales, bajar el ZIP manualmente desde la página de Kaggle
y dejar creditcard.csv dentro de la carpeta data/.
"""
import shutil
from pathlib import Path

import kagglehub

from src.config import DATASET_KAGGLE, DIR_DATOS, RUTA_CSV


def descargar() -> Path:
    """Descarga el CSV si no existe todavía y devuelve su ruta."""
    if RUTA_CSV.exists():
        print(f"El dataset ya existe en {RUTA_CSV}, no se descarga de nuevo.")
        return RUTA_CSV

    # kagglehub descarga a su propia caché y devuelve la carpeta donde quedó el dataset
    print(f"Descargando {DATASET_KAGGLE} desde Kaggle (~150 MB)...")
    carpeta_cache = Path(kagglehub.dataset_download(DATASET_KAGGLE))

    origen = carpeta_cache / "creditcard.csv"
    if not origen.exists():
        raise FileNotFoundError(f"No se encontró creditcard.csv en {carpeta_cache}")

    # Copiamos a data/ para que todo el proyecto use la misma ruta (definida en config.py)
    DIR_DATOS.mkdir(parents=True, exist_ok=True)
    shutil.copy(origen, RUTA_CSV)
    print(f"Dataset guardado en {RUTA_CSV}")
    return RUTA_CSV


if __name__ == "__main__":
    descargar()
