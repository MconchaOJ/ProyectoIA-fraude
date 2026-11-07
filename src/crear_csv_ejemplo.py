"""
Crea data/ejemplo_transacciones.csv: una muestra pequeña del conjunto de VALIDACIÓN para la demo de la interfaz.

Uso (desde la raíz del proyecto):
    python -m src.crear_csv_ejemplo

Contenido: TODOS los fraudes de validación (71) + transacciones legítimas al azar hasta completar 2.000 filas,
mezcladas, con la columna Class incluida (para que la interfaz pueda calcular métricas).

Por qué validación y no prueba:
  - El conjunto de prueba se usa UNA sola vez, al final, para el reporte. Si lo usáramos en la demo
    estaríamos mirando sus resultados una y otra vez (y moviendo el umbral sobre él), lo que equivale a
    tomar decisiones con la prueba y vuelve optimista la métrica final.
  - Tampoco entrenamiento: el modelo ya vio esas filas y sus resultados serían mejores que con datos nuevos.
  - Validación no se usó para entrenar, y es justamente el conjunto donde está permitido explorar umbrales.

OJO al interpretar la demo: la muestra tiene ~3,6 % de fraudes (71 de 2.000), unas 20 veces más que el
dataset real (0,167 %). El recall no depende de esa proporción, pero la PRECISIÓN sale más alta que en
la realidad, porque hay menos legítimas que puedan convertirse en falsas alarmas.
"""
import pandas as pd

from src.config import COLUMNA_OBJETIVO, DIR_DATOS, RANDOM_STATE
from src.datos import cargar_datos, particionar

N_FILAS = 2000
RUTA_EJEMPLO = DIR_DATOS / "ejemplo_transacciones.csv"


def crear_csv_ejemplo():
    df = cargar_datos()
    _, X_val, _, _, y_val, _ = particionar(df)  # misma partición de siempre; solo usamos validación
    val = X_val.assign(**{COLUMNA_OBJETIVO: y_val})

    fraudes = val[val[COLUMNA_OBJETIVO] == 1]
    legitimas = val[val[COLUMNA_OBJETIVO] == 0].sample(n=N_FILAS - len(fraudes), random_state=RANDOM_STATE)

    # frac=1 mezcla las filas, para que los fraudes no queden todos al principio
    ejemplo = pd.concat([fraudes, legitimas]).sample(frac=1, random_state=RANDOM_STATE)
    ejemplo.to_csv(RUTA_EJEMPLO, index=False)

    print(f"Guardado {RUTA_EJEMPLO}: {len(ejemplo)} filas, {len(fraudes)} fraudes "
          f"({100 * len(fraudes) / len(ejemplo):.2f} %), tomadas del conjunto de VALIDACIÓN")


if __name__ == "__main__":
    crear_csv_ejemplo()
