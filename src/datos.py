"""
Carga y limpieza del dataset. Todo notebook, script o la interfaz que necesite los datos
debe pasar por aquí, para que el baseline y los modelos usen EXACTAMENTE las mismas filas.

Uso:
    from src.datos import cargar_datos
    df = cargar_datos()            # carga y elimina duplicados (lo normal)

    X_train, X_val, X_test, y_train, y_val, y_test = particionar(df)
"""
import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import COLUMNA_OBJETIVO, PROP_TEST, PROP_VAL, RANDOM_STATE, RUTA_CSV


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


def particionar(df: pd.DataFrame):
    """
    Partición estratificada 70/15/15 (train/val/test) con semilla fija.

    train_test_split solo divide en DOS partes, por eso se hace en dos pasos:
      1) df -> train (70%) + temporal (30%)          test_size = PROP_VAL + PROP_TEST = 0.30
      2) temporal -> val (15%) + test (15%)          test_size = PROP_TEST / 0.30 = 0.50
         (la mitad del 30% es el 15% del total)

    stratify=y en AMBOS pasos: así cada conjunto conserva la misma proporción de fraudes (~0,167%).
    Sin estratificar, con solo 473 fraudes, val o test podrían quedar con bastantes menos fraudes
    por azar y las métricas serían poco confiables.

    Devuelve X_train, X_val, X_test, y_train, y_val, y_test.
    """
    X = df.drop(columns=COLUMNA_OBJETIVO)
    y = df[COLUMNA_OBJETIVO]

    prop_temporal = PROP_VAL + PROP_TEST  # 0.30
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=prop_temporal, stratify=y, random_state=RANDOM_STATE
    )

    prop_test_en_temporal = PROP_TEST / prop_temporal  # 0.15 / 0.30 = 0.50
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=prop_test_en_temporal, stratify=y_temp, random_state=RANDOM_STATE
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def tabla_particion(y_train, y_val, y_test) -> pd.DataFrame:
    """Tabla con filas, fraudes, % de fraude y % del total de cada conjunto (para verificar la estratificación)."""
    total = len(y_train) + len(y_val) + len(y_test)
    filas = []
    for nombre, y in [("train", y_train), ("val", y_val), ("test", y_test)]:
        filas.append({
            "conjunto": nombre,
            "filas": len(y),
            "% del total": round(100 * len(y) / total, 2),
            "fraudes": int(y.sum()),
            "% fraude": round(100 * y.mean(), 4),
        })
    return pd.DataFrame(filas)
