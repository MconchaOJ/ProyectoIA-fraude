"""
Definición de los pipelines de todos los modelos del proyecto (Baseline y Avance 2).
Centralizado aquí para que los scripts de entrenamiento, notebooks y la interfaz de Streamlit
usen exactamente la misma configuración sin discrepancias.

Modelos incluidos:
1. Baseline: Regresión logística sin balanceo (StandardScaler + LogisticRegression).
2. Balanceado: Regresión logística con ponderación de clases (class_weight='balanced').
3. Remuestreo: Regresión logística con SMOTE aplicado solo en entrenamiento (imblearn.Pipeline).
4. No lineal (Ensamble): Random Forest balanceado con árboles de profundidad controlada.
5. No supervisado: Isolation Forest con normalización de puntaje de anomalía para detección de casos atípicos.
"""
from typing import Union

import numpy as np
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import RANDOM_STATE


class IsolationForestWrapper(BaseEstimator, ClassifierMixin):
    """
    Adaptador para Isolation Forest que expone una interfaz predict_proba() compatible con Scikit-Learn y Streamlit.
    Convierte los puntajes brutos de anomalía (-score_samples) en un score continuo acotado [0, 1].
    """
    def __init__(self, n_estimators: int = 100, contamination: float = 0.0017, random_state: int = RANDOM_STATE):
        self.n_estimators = n_estimators
        self.contamination = contamination
        self.random_state = random_state
        self.modelo_ = None
        self.min_score_ = None
        self.max_score_ = None

    def fit(self, X, y=None):
        self.modelo_ = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.modelo_.fit(X)
        # Calcular límites empíricos en train para normalizar min-max
        raw_scores = -self.modelo_.score_samples(X)
        self.min_score_ = float(np.percentile(raw_scores, 0.1))
        self.max_score_ = float(np.percentile(raw_scores, 99.9))
        return self

    def predict_proba(self, X):
        raw_scores = -self.modelo_.score_samples(X)
        rango = self.max_score_ - self.min_score_
        if rango <= 0:
            prob = np.zeros(len(X))
        else:
            prob = np.clip((raw_scores - self.min_score_) / rango, 0.0, 1.0)
        return np.column_stack([1.0 - prob, prob])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


def crear_logistica_sin_balanceo() -> Pipeline:
    """Baseline: StandardScaler + regresión logística SIN balanceo."""
    return Pipeline([
        ("escalado", StandardScaler()),
        ("modelo", LogisticRegression(solver="lbfgs", C=1.0, max_iter=1000, random_state=RANDOM_STATE)),
    ])


def crear_logistica_balanceada() -> Pipeline:
    """Técnica 1: Regresión logística con ponderación inversa de clases (class_weight='balanced')."""
    return Pipeline([
        ("escalado", StandardScaler()),
        ("modelo", LogisticRegression(solver="lbfgs", C=1.0, max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)),
    ])


def crear_logistica_smote() -> ImbPipeline:
    """
    Técnica 2: Regresión logística con sobremuestreo sintético de la clase minoritaria (SMOTE).
    Usa imblearn.pipeline para garantizar que SMOTE se aplique EXCLUSIVAMENTE durante fit() en Train.
    """
    return ImbPipeline([
        ("escalado", StandardScaler()),
        ("smote", SMOTE(random_state=RANDOM_STATE)),
        ("modelo", LogisticRegression(solver="lbfgs", C=1.0, max_iter=1000, random_state=RANDOM_STATE)),
    ])


def crear_random_forest() -> Pipeline:
    """
    Técnica 3: Ensamble no lineal (Random Forest) con árboles de decisión balanceados.
    max_depth=12 evita sobreajuste y mantiene tiempo de entrenamiento rápido (~8 s).
    """
    return Pipeline([
        ("modelo", RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1
        )),
    ])


def crear_isolation_forest() -> Pipeline:
    """
    Técnica 4: Detección no supervisada de anomalías (Isolation Forest).
    No utiliza las etiquetas de fraude durante el entrenamiento.
    """
    return Pipeline([
        ("escalado", StandardScaler()),
        ("modelo", IsolationForestWrapper(
            n_estimators=100,
            contamination=0.0017,
            random_state=RANDOM_STATE
        )),
    ])
