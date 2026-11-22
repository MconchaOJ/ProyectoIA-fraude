"""
Entrena sistemáticamente todos los modelos del proyecto (Baseline y Avance 2),
evalúa su desempeño sobre el conjunto de validación (42.559 transacciones, 71 fraudes reales)
y exporta los artefactos necesarios para la interfaz en Streamlit y la documentación técnica.

Modelos evaluados:
1. Baseline: Regresión logística sin balanceo
2. Regresión logística con ponderación inversa de clases (class_weight='balanced')
3. Regresión logística con remuestreo sintético (SMOTE solo en train)
4. Ensamble no lineal: Random Forest balanceado
5. Detección no supervisada: Isolation Forest

Genera:
- models/*.joblib y models/*.json para cada modelo
- docs/resultados_modelos_val.csv con la tabla comparativa de métricas
- docs/capturas/03_comparacion_curvas_pr.png con la comparativa visual de curvas PR
"""
import json
import time
from datetime import datetime
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn

from src.config import DIR_CAPTURAS, DIR_DOCS, DIR_MODELOS, RANDOM_STATE
from src.datos import cargar_datos, particionar
from src.evaluacion import evaluar, graficar_curva_pr
from src.modelos import (
    crear_isolation_forest,
    crear_logistica_balanceada,
    crear_logistica_sin_balanceo,
    crear_logistica_smote,
    crear_random_forest,
)

UMBRALES_TABLA = [0.9, 0.5, 0.3, 0.1, 0.05, 0.01]


def calcular_tabla_umbrales(y_val, puntaje_val, umbrales=UMBRALES_TABLA) -> list:
    """Precalcula métricas para una lista de umbrales en validación."""
    filas = []
    for u in umbrales:
        r = evaluar(y_val, puntaje_val, umbral=u)
        filas.append({
            "umbral": u,
            "alertas": int(r["TP"] + r["FP"]),
            "TP": int(r["TP"]),
            "FP": int(r["FP"]),
            "FN": int(r["FN"]),
            "precision": round(float(r["precision"]), 4),
            "recall": round(float(r["recall"]), 4),
            "F1": round(float(r["F1"]), 4),
        })
    return filas


def entrenar_todos():
    print("=" * 70)
    print("INICIANDO ENTRENAMIENTO Y BENCHMARK DE AVANCE 2 (5 MODELOS)")
    print("=" * 70)

    # 1. Cargar y particionar datos
    df = cargar_datos()
    X_train, X_val, X_test, y_train, y_val, y_test = particionar(df)
    print(f"Partición estratificada lista (semilla {RANDOM_STATE}):")
    print(f"  Train:      {len(X_train):>7} filas | {int(y_train.sum()):>3} fraudes ({y_train.mean()*100:.3f} %)")
    print(f"  Validación: {len(X_val):>7} filas | {int(y_val.sum()):>3} fraudes ({y_val.mean()*100:.3f} %)")
    print(f"  Prueba:     {len(X_test):>7} filas | {int(y_test.sum()):>3} fraudes ({y_test.mean()*100:.3f} %) [SELLADA]")
    print("-" * 70)

    definiciones_modelos = [
        {
            "id": "logistica_sin_balanceo",
            "nombre_ui": "Regresión logística (Baseline sin balanceo)",
            "descripcion": "Baseline 2: StandardScaler + LogisticRegression estándar",
            "creador": crear_logistica_sin_balanceo,
            "tipo": "Supervisado lineal",
            "balanceo": "Ninguno",
        },
        {
            "id": "logistica_balanceada",
            "nombre_ui": "Regresión logística (class_weight='balanced')",
            "descripcion": "Técnica 1: Ponderación inversa de clases en la función de costo",
            "creador": crear_logistica_balanceada,
            "tipo": "Supervisado lineal",
            "balanceo": "Ponderación (class_weight)",
        },
        {
            "id": "logistica_smote",
            "nombre_ui": "Regresión logística con SMOTE",
            "descripcion": "Técnica 2: Sobremuestreo sintético aplicado exclusivamente a Train",
            "creador": crear_logistica_smote,
            "tipo": "Supervisado lineal",
            "balanceo": "Sobremuestreo (SMOTE)",
        },
        {
            "id": "random_forest",
            "nombre_ui": "Random Forest (Ensamble balanceado)",
            "descripcion": "Técnica 3: Ensamble de 100 árboles de decisión no lineales (max_depth=12)",
            "creador": crear_random_forest,
            "tipo": "Supervisado no lineal",
            "balanceo": "Ponderación (class_weight)",
        },
        {
            "id": "isolation_forest",
            "nombre_ui": "Isolation Forest (No supervisado)",
            "descripcion": "Técnica 4: Aislamiento estocástico de anomalías sin usar etiquetas de fraude",
            "creador": crear_isolation_forest,
            "tipo": "No supervisado",
            "balanceo": "No aplica",
        },
    ]

    DIR_MODELOS.mkdir(parents=True, exist_ok=True)
    DIR_DOCS.mkdir(parents=True, exist_ok=True)
    DIR_CAPTURAS.mkdir(parents=True, exist_ok=True)

    resumen_filas = []
    dict_puntajes_pr = {}

    for config in definiciones_modelos:
        mid = config["id"]
        print(f"\n>>> Entrenando: {config['nombre_ui']}...")
        pipeline = config["creador"]()

        t_inicio = time.perf_counter()
        pipeline.fit(X_train, y_train)
        t_entrenamiento = time.perf_counter() - t_inicio

        # Inferencia en validación
        puntaje_val = pipeline.predict_proba(X_val)[:, 1]
        dict_puntajes_pr[config["nombre_ui"]] = puntaje_val

        # Métricas estándar (umbral 0.5)
        res_val = evaluar(y_val, puntaje_val, umbral=0.5)
        metricas_limpias = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in res_val.items() if k != "matriz"}

        print(f"    Completado en {t_entrenamiento:.2f} s")
        print(f"    AUPRC: {metricas_limpias['AUPRC']:.4f} | Recall (0.5): {metricas_limpias['recall']:.4f} | Precisión (0.5): {metricas_limpias['precision']:.4f}")
        print(f"    Aciertos: TP={metricas_limpias['TP']}/71 | Falsas alarmas: FP={metricas_limpias['FP']}")

        # Metadatos del modelo
        metadatos = {
            "id": mid,
            "nombre": config["nombre_ui"],
            "descripcion": config["descripcion"],
            "tipo": config["tipo"],
            "balanceo": config["balanceo"],
            "fecha_entrenamiento": datetime.now().isoformat(timespec="seconds"),
            "columnas": list(X_train.columns),
            "random_state": RANDOM_STATE,
            "metricas_val": metricas_limpias,
            "umbrales_val": calcular_tabla_umbrales(y_val, puntaje_val),
            "tiempo_entrenamiento_s": round(t_entrenamiento, 3),
            "version_sklearn": sklearn.__version__,
        }

        # Guardar binario y json
        ruta_joblib = DIR_MODELOS / f"{mid}.joblib"
        validacion_pack = {"y": y_val.to_numpy(), "puntaje": puntaje_val}
        joblib.dump({"modelo": pipeline, "metadatos": metadatos, "validacion": validacion_pack}, ruta_joblib)

        ruta_json = DIR_MODELOS / f"{mid}.json"
        ruta_json.write_text(json.dumps(metadatos, indent=2, ensure_ascii=False), encoding="utf-8")

        resumen_filas.append({
            "Modelo": config["nombre_ui"],
            "Tipo": config["tipo"],
            "Manejo Desbalance": config["balanceo"],
            "AUPRC": metricas_limpias["AUPRC"],
            "Recall (0.5)": metricas_limpias["recall"],
            "Precisión (0.5)": metricas_limpias["precision"],
            "F1 (0.5)": metricas_limpias["F1"],
            "TP (0.5)": metricas_limpias["TP"],
            "FP (0.5)": metricas_limpias["FP"],
            "Tiempo (s)": round(t_entrenamiento, 2),
        })

    # 2. Guardar tabla comparativa en CSV
    df_resumen = pd.DataFrame(resumen_filas)
    ruta_csv_resumen = DIR_DOCS / "resultados_modelos_val.csv"
    df_resumen.to_csv(ruta_csv_resumen, index=False)
    print("\n" + "=" * 70)
    print("TABLA COMPARATIVA EN VALIDACIÓN (Guardada en docs/resultados_modelos_val.csv):")
    print(df_resumen.to_string(index=False))

    # 3. Graficar comparativa de Curvas PR
    ruta_curva_png = DIR_CAPTURAS / "03_comparacion_curvas_pr.png"
    fig, ax = plt.subplots(figsize=(8, 6))
    graficar_curva_pr(
        y_val,
        dict_puntajes_pr,
        titulo="Comparativa de Modelos en Validación — Curvas Precisión-Recall",
        ruta=ruta_curva_png,
        ax=ax,
    )
    plt.close(fig)
    print(f"\nGráfico comparativo de curvas PR guardado en: {ruta_curva_png}")
    print("=" * 70)
    print("¡TODOS LOS MODELOS DE AVANCE 2 HAN SIDO ENTRENADOS Y SERIALIZADOS CON ÉXITO!")


if __name__ == "__main__":
    entrenar_todos()
