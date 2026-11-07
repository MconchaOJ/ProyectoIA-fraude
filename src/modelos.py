"""
Definición de los pipelines de los modelos. Se definen aquí, en un solo lugar, para que el notebook,
el script de entrenamiento y (en el Avance 2) los modelos nuevos usen exactamente la misma configuración.

En el Avance 2 se agregarán aquí: regresión logística con class_weight, con SMOTE (imblearn.Pipeline),
Random Forest, Isolation Forest y Naive Bayes.
"""
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def crear_logistica_sin_balanceo() -> Pipeline:
    """
    Baseline 2: StandardScaler + regresión logística SIN manejo del desbalance.
    Mismos hiperparámetros que el notebook 02_baseline (sección 4).
    """
    return Pipeline([
        ("escalado", StandardScaler()),  # se ajusta solo con los datos que reciba fit() (train)
        ("modelo", LogisticRegression(solver="lbfgs", C=1.0, max_iter=1000)),
    ])
