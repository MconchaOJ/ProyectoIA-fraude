"""
Entrena el baseline 2 (regresión logística sin balanceo) y lo guarda para que lo use la interfaz.

Uso (desde la raíz del proyecto):
    python -m src.entrenar_baseline

Genera:
    models/logistica_sin_balanceo.joblib   -> {"modelo": pipeline entrenado, "metadatos": {...}}  (no se versiona)
    models/logistica_sin_balanceo.json     -> los mismos metadatos en texto legible           (sí se versiona)

Por qué un script y no solo el notebook: así cualquiera puede regenerar el modelo desde cero con un
comando, sin depender del estado de un notebook. La interfaz siempre carga un archivo producido por aquí.
"""
import json
import time
from datetime import datetime

import joblib
import sklearn

from src.config import DIR_MODELOS, RANDOM_STATE
from src.datos import cargar_datos, particionar
from src.evaluacion import evaluar
from src.modelos import crear_logistica_sin_balanceo

NOMBRE = "logistica_sin_balanceo"
UMBRAL_POR_DEFECTO = 0.5


def entrenar_y_guardar():
    # 1. Mismos datos y misma partición que el notebook 02 (sin duplicados, 70/15/15, semilla 42)
    df = cargar_datos()
    X_train, X_val, X_test, y_train, y_val, y_test = particionar(df)

    # 2. Entrenar SOLO con train
    modelo = crear_logistica_sin_balanceo()
    inicio = time.perf_counter()
    modelo.fit(X_train, y_train)
    tiempo = time.perf_counter() - inicio

    # 3. Evaluar en validación (el conjunto de prueba NO se usa aquí)
    puntaje_val = modelo.predict_proba(X_val)[:, 1]
    res = evaluar(y_val, puntaje_val, umbral=UMBRAL_POR_DEFECTO)
    metricas_val = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res.items() if k != "matriz"}

    # 4. Metadatos: lo que la interfaz (y el equipo) necesita saber del modelo sin reentrenarlo
    hiper = modelo.named_steps["modelo"].get_params()
    metadatos = {
        "nombre": NOMBRE,
        "descripcion": "Regresión logística sin manejo del desbalance (baseline 2)",
        "fecha_entrenamiento": datetime.now().isoformat(timespec="seconds"),
        "columnas": list(X_train.columns),  # columnas que debe traer el CSV, en este orden
        "puntaje": "predict_proba(X)[:, 1]",
        "umbral_por_defecto": UMBRAL_POR_DEFECTO,
        "hiperparametros": {"escalado": "StandardScaler", "solver": hiper["solver"],
                            "C": hiper["C"], "max_iter": hiper["max_iter"]},
        "random_state": RANDOM_STATE,
        "particion": {"train": len(y_train), "val": len(y_val), "test": len(y_test),
                      "fraudes_train": int(y_train.sum()), "fraudes_val": int(y_val.sum())},
        "metricas_val": metricas_val,
        "tiempo_entrenamiento_s": round(tiempo, 3),
        "version_sklearn": sklearn.__version__,  # un .joblib solo es confiable con la misma versión
    }

    # 5. Guardar
    DIR_MODELOS.mkdir(parents=True, exist_ok=True)
    ruta_modelo = DIR_MODELOS / f"{NOMBRE}.joblib"
    joblib.dump({"modelo": modelo, "metadatos": metadatos}, ruta_modelo)
    (DIR_MODELOS / f"{NOMBRE}.json").write_text(json.dumps(metadatos, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Modelo guardado en {ruta_modelo} (entrenado en {tiempo:.2f} s)")
    print("Métricas en validación (umbral 0,5):")
    for k in ["AUPRC", "precision", "recall", "F1", "accuracy", "TP", "FP", "FN", "TN"]:
        print(f"  {k:10s} {metricas_val[k]}")


if __name__ == "__main__":
    entrenar_y_guardar()
