"""
Métricas y gráficos de evaluación. Todos los modelos (baseline, Avance 2 e interfaz) se evalúan
con estas mismas funciones, así la comparación es justa.

Convención: "puntaje" = puntaje de riesgo de fraude. Mientras más alto, más sospechosa la transacción.
  - Modelos supervisados: modelo.predict_proba(X)[:, 1]
  - Isolation Forest (Avance 2): -modelo.score_samples(X)
"""
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)


def evaluar(y_true, puntaje, umbral: float = 0.5) -> dict:
    """
    Calcula las métricas de un modelo.

    - AUPRC (average_precision_score) usa el PUNTAJE continuo: resume la curva Precisión-Recall
      para todos los umbrales posibles. NO depende del umbral elegido.
    - Precisión, recall, F1, accuracy y matriz de confusión usan la DECISIÓN binaria:
      alerta (1) si puntaje >= umbral, aprobar (0) si no. SÍ dependen del umbral.

    zero_division=0: si el modelo nunca alerta, la precisión sería 0/0; se informa como 0
    en vez de lanzar una advertencia (caso del DummyClassifier).
    """
    y_true = np.asarray(y_true)
    puntaje = np.asarray(puntaje)
    y_pred = (puntaje >= umbral).astype(int)

    # labels=[0, 1] fuerza una matriz 2x2 aunque el modelo nunca prediga fraude
    matriz = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = matriz.ravel()

    return {
        "AUPRC": average_precision_score(y_true, puntaje),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "F1": f1_score(y_true, y_pred, zero_division=0),
        "accuracy": accuracy_score(y_true, y_pred),
        "TP": int(tp), "FP": int(fp), "FN": int(fn), "TN": int(tn),
        "matriz": matriz,
    }


def graficar_curva_pr(y_true, puntajes: dict, titulo: str = "Curva Precisión-Recall", ruta=None, ax=None):
    """
    Grafica la curva PR de uno o más modelos. puntajes = {"nombre modelo": puntaje, ...}

    La línea punteada horizontal es el clasificador ALEATORIO: su precisión es igual a la
    proporción de fraudes en cualquier umbral, así que su AUPRC ≈ proporción de fraudes.
    Un modelo útil debe quedar claramente por encima de esa línea.
    """
    y_true = np.asarray(y_true)
    prevalencia = y_true.mean()

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))

    for nombre, puntaje in puntajes.items():
        precision, recall, _ = precision_recall_curve(y_true, puntaje)
        ap = average_precision_score(y_true, puntaje)
        # drawstyle="steps-post" dibuja la curva en escalera, que es como la calcula average_precision_score
        ax.plot(recall, precision, drawstyle="steps-post", linewidth=2, label=f"{nombre} (AUPRC = {ap:.3f})")

    ax.axhline(prevalencia, color="gray", linestyle="--", linewidth=1.5,
               label=f"Aleatorio (AUPRC ≈ {prevalencia:.4f})")
    ax.set_xlabel("Recall (fraudes detectados / fraudes reales)")
    ax.set_ylabel("Precisión (fraudes reales / alertas)")
    ax.set_xlim(0, 1.01)
    ax.set_ylim(0, 1.05)
    ax.set_title(titulo)
    ax.legend(loc="lower left", fontsize=9)

    if ruta is not None:
        ax.figure.tight_layout()
        ax.figure.savefig(ruta, dpi=150)
    return ax


def graficar_matriz_confusion(matriz, titulo: str = "Matriz de confusión", ruta=None, ax=None):
    """Dibuja una matriz de confusión 2x2 con etiquetas en español (filas = real, columnas = predicho)."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(4.5, 4))
    disp = ConfusionMatrixDisplay(matriz, display_labels=["Legítima", "Fraude"])
    disp.plot(ax=ax, cmap="Blues", values_format="d", colorbar=False)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")
    ax.set_title(titulo)
    ax.grid(False)

    if ruta is not None:
        ax.figure.tight_layout()
        ax.figure.savefig(ruta, dpi=150)
    return ax
