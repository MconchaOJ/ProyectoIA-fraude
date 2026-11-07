"""
Carga y limpieza del dataset. Todo notebook, script o la interfaz que necesite los datos
debe pasar por aquí, para que el baseline y los modelos usen EXACTAMENTE las mismas filas.

Uso:
    from src.datos import cargar_datos
    df = cargar_datos()            # carga y elimina duplicados (lo normal)

La partición train/val/test se agregará en este mismo archivo (notebook 02_baseline).
"""
import pandas as pd

from src.config import COLUMNA_OBJETIVO, RUTA_CSV


def resumen_clases(df: pd.DataFrame) -> dict:
    """Cuenta transacciones, fraudes y el % de fraude de un DataFrame."""
    n_total = len(df)
    n_fraudes = int(df[COLUMNA_OBJETIVO].sum())
    return {
        "filas": n_total,
        "fraudes": n_fraudes,
        "legitimas": n_total - n_fraudes,
        "pct_fraude": 100 * n_fraudes / n_total,
    }


def eliminar_duplicados(df: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Elimina filas idénticas en TODAS las columnas (Time, V1-V28, Amount y Class).

    Por qué: si una fila y su copia caen una en entrenamiento y otra en prueba, el modelo
    "ya vio" esa transacción de prueba (fuga de información) y las métricas salen infladas.
    Por eso se eliminan ANTES de la partición.

    Se conserva la primera aparición (keep="first") y se reinicia el índice para que
    quede correlativo (0, 1, 2, ...).
    """
    mascara_dup = df.duplicated(keep="first")  # True en las copias, no en la original

    if verbose:
        dups = df[mascara_dup]
        antes = resumen_clases(df)
        print(f"Filas duplicadas a eliminar: {len(dups)}")
        print(f"  - legítimas: {int((dups[COLUMNA_OBJETIVO] == 0).sum())}")
        print(f"  - fraudes:   {int((dups[COLUMNA_OBJETIVO] == 1).sum())}")
        print(f"Antes:   {antes['filas']} filas, {antes['fraudes']} fraudes ({antes['pct_fraude']:.3f}%)")

    df_limpio = df[~mascara_dup].reset_index(drop=True)

    if verbose:
        despues = resumen_clases(df_limpio)
        print(f"Después: {despues['filas']} filas, {despues['fraudes']} fraudes ({despues['pct_fraude']:.3f}%)")

    return df_limpio


def cargar_datos(ruta=RUTA_CSV, quitar_duplicados: bool = True, verbose: bool = False) -> pd.DataFrame:
    """
    Lee creditcard.csv y, por defecto, elimina los duplicados.

    quitar_duplicados=False solo se usa en la exploración, para mostrar los datos originales.
    """
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}. Ejecuta primero: python -m src.descargar_datos"
        )
    df = pd.read_csv(ruta)
    if quitar_duplicados:
        df = eliminar_duplicados(df, verbose=verbose)
    return df
