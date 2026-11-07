"""
Interfaz Streamlit — Detección de fraude en transacciones bancarias (Tema 12). BORRADOR del Avance 1.

Ejecutar desde la raíz del proyecto:
    streamlit run app/app.py

Flujo: CSV -> validación de columnas -> modelo (pipeline con escalado) -> puntaje de riesgo
       -> umbral (slider) -> aprobar / alertar -> métricas (solo si el CSV trae la columna Class).

Cómo funciona Streamlit (importante para entender este archivo): cada vez que el usuario toca algo
(mueve el slider, sube un archivo, cambia de sección) Streamlit vuelve a ejecutar el script COMPLETO de
arriba a abajo. Por eso lo caro (cargar el modelo, calcular puntajes) se guarda en caché.
"""
import json
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Para poder importar src/ (la app está en app/, un nivel bajo la raíz)
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.config import COLUMNA_OBJETIVO, DIR_DATOS, DIR_MODELOS  # noqa: E402
from src.evaluacion import evaluar, graficar_matriz_confusion  # noqa: E402

# Modelos disponibles: nombre visible -> archivo en models/.
# Avance 2: agregar aquí una línea por modelo nuevo (p. ej. "Random Forest + SMOTE": "rf_smote.joblib").
MODELOS = {
    "Regresión logística (sin balanceo) — baseline": "logistica_sin_balanceo.joblib",
}
RUTA_EJEMPLO = DIR_DATOS / "ejemplo_transacciones.csv"
AVISO = "⚠️ Resultados académicos; no constituyen una decisión sobre clientes reales."


# ------------------------------------------------------------------ Funciones con caché
@st.cache_resource
def cargar_modelo(nombre_archivo: str):
    """
    Carga {"modelo", "metadatos"} desde models/.
    cache_resource: el modelo se carga UNA vez y se comparte entre ejecuciones del script y usuarios.
    Sin esto, cada movimiento del slider volvería a leer el archivo desde el disco.
    """
    return joblib.load(DIR_MODELOS / nombre_archivo)


@st.cache_data
def calcular_puntajes(nombre_archivo: str, X: pd.DataFrame):
    """
    Puntaje de riesgo = probabilidad de fraude. cache_data: para el mismo modelo y los mismos datos
    no se recalcula; al mover el slider solo cambia la comparación puntaje >= umbral, que es instantánea.
    """
    modelo = cargar_modelo(nombre_archivo)["modelo"]
    return modelo.predict_proba(X)[:, 1]


def validar_columnas(df: pd.DataFrame, columnas_esperadas: list):
    """Devuelve una lista de problemas (vacía si el CSV sirve)."""
    problemas = []
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        problemas.append(f"Faltan {len(faltantes)} columnas: {', '.join(faltantes)}")
        return problemas  # sin las columnas no tiene sentido seguir revisando
    no_numericas = [c for c in columnas_esperadas if not pd.api.types.is_numeric_dtype(df[c])]
    if no_numericas:
        problemas.append(f"Columnas no numéricas: {', '.join(no_numericas)}")
    con_nulos = [c for c in columnas_esperadas if df[c].isna().any()]
    if con_nulos:
        problemas.append(f"Columnas con valores vacíos: {', '.join(con_nulos)}")
    if COLUMNA_OBJETIVO in df.columns and not df[COLUMNA_OBJETIVO].isin([0, 1]).all():
        problemas.append(f"La columna {COLUMNA_OBJETIVO} solo puede tener valores 0 o 1")
    return problemas


# ------------------------------------------------------------------ Estructura general
st.set_page_config(page_title="Detección de fraude — Tema 12", page_icon="🛡️", layout="wide")
st.title("🛡️ Detección de fraude en transacciones bancarias")
st.warning(AVISO)  # aviso ético visible en todas las secciones

st.sidebar.header("Menú")
seccion = st.sidebar.radio(
    "Sección", ["Analizar transacciones", "Resultados del modelo", "Acerca del proyecto"]
)

# Selector de modelo: solo muestra los que existen en models/ (los del Avance 2 aparecerán al entrenarlos)
disponibles = {nombre: archivo for nombre, archivo in MODELOS.items() if (DIR_MODELOS / archivo).exists()}
if not disponibles:
    st.error("No hay modelos entrenados en models/. Ejecuta primero: `python -m src.entrenar_baseline`")
    st.stop()
nombre_modelo = st.sidebar.selectbox("Modelo", list(disponibles))
archivo_modelo = disponibles[nombre_modelo]
metadatos = cargar_modelo(archivo_modelo)["metadatos"]
st.sidebar.caption(f"Entrenado: {metadatos['fecha_entrenamiento']}")


# ------------------------------------------------------------------ Sección 1: Analizar transacciones
def seccion_analizar():
    st.header("Analizar transacciones")

    # --- 1. Entrada: CSV del usuario o el de ejemplo
    archivo = st.file_uploader("Sube un CSV con transacciones", type="csv")
    usar_ejemplo = st.checkbox(
        "Usar el CSV de ejemplo (2.000 transacciones del conjunto de validación, con Class)",
        value=archivo is None,
    )
    if archivo is not None and not usar_ejemplo:
        df = pd.read_csv(archivo)
    elif usar_ejemplo and RUTA_EJEMPLO.exists():
        df = pd.read_csv(RUTA_EJEMPLO)
        st.info("CSV de ejemplo: tiene ~3,6 % de fraudes, unas 20 veces más que la realidad (0,167 %). "
                "El recall es comparable, pero la precisión sale más alta que en un banco real.")
    else:
        st.info("Sube un CSV o marca la opción del CSV de ejemplo para comenzar.")
        return

    # --- 2. Validación de columnas
    columnas = metadatos["columnas"]
    problemas = validar_columnas(df, columnas)
    if problemas:
        st.error("El CSV no tiene el formato esperado:\n\n- " + "\n- ".join(problemas))
        st.caption("Columnas requeridas: " + ", ".join(columnas) + f". Opcional: {COLUMNA_OBJETIVO}.")
        return
    tiene_clase = COLUMNA_OBJETIVO in df.columns
    st.success(f"CSV válido: {len(df):,} transacciones".replace(",", ".")
               + (" (con etiquetas Class: se calcularán métricas)" if tiene_clase else " (sin Class: solo puntajes y alertas)"))

    # --- 3. Puntaje de riesgo (el pipeline escala internamente con la media/desv. de entrenamiento)
    puntaje = calcular_puntajes(archivo_modelo, df[columnas])

    # --- 4. Umbral: alertar si puntaje >= umbral
    umbral = st.slider("Umbral de decisión (alertar si puntaje ≥ umbral)", 0.0, 1.0,
                       float(metadatos["umbral_por_defecto"]), step=0.01,
                       help="Umbral bajo: detecta más fraudes pero genera más falsas alarmas. Umbral alto: lo contrario.")
    alerta = puntaje >= umbral

    c1, c2 = st.columns(2)
    c1.metric("Alertas", int(alerta.sum()))
    c2.metric("Aprobadas", int((~alerta).sum()))

    # --- 5. Métricas en vivo (solo si hay etiquetas reales)
    if tiene_clase:
        res = evaluar(df[COLUMNA_OBJETIVO], puntaje, umbral=umbral)
        st.subheader("Métricas con este umbral")
        m = st.columns(6)
        m[0].metric("TP (fraudes detectados)", res["TP"])
        m[1].metric("FP (falsas alarmas)", res["FP"])
        m[2].metric("FN (fraudes no detectados)", res["FN"])
        m[3].metric("TN", res["TN"])
        m[4].metric("Precisión", f"{res['precision']:.3f}")
        m[5].metric("Recall", f"{res['recall']:.3f}")
        st.caption(f"AUPRC en este CSV: {res['AUPRC']:.3f} (no depende del umbral). "
                   f"Accuracy: {res['accuracy']:.4f} (se muestra solo para contrastar: engaña con datos desbalanceados).")

        fig, ax = plt.subplots(figsize=(4, 3.5))
        graficar_matriz_confusion(res["matriz"], titulo=f"Matriz de confusión (umbral {umbral:.2f})", ax=ax)
        col_fig, _ = st.columns([1, 2])  # columna angosta para que la figura no ocupe todo el ancho
        col_fig.pyplot(fig)
        plt.close(fig)

    # --- 6. Tabla ordenada por riesgo
    st.subheader("Transacciones ordenadas por puntaje de riesgo")
    tabla = df.assign(puntaje_riesgo=puntaje, decision=["ALERTA" if a else "Aprobar" for a in alerta])
    columnas_tabla = ["puntaje_riesgo", "decision", "Time", "Amount"] + ([COLUMNA_OBJETIVO] if tiene_clase else [])
    st.dataframe(
        tabla.sort_values("puntaje_riesgo", ascending=False)[columnas_tabla],
        column_config={"puntaje_riesgo": st.column_config.NumberColumn("Puntaje de riesgo", format="%.4f")},
        height=400,
    )


# ------------------------------------------------------------------ Sección 2: Resultados del modelo
def seccion_resultados():
    st.header("Resultados del modelo")
    st.write(f"**{metadatos['descripcion']}**")

    st.subheader("Métricas en validación (umbral 0,5)")
    mv = metadatos["metricas_val"]
    st.dataframe(pd.DataFrame([{k: mv[k] for k in ["AUPRC", "precision", "recall", "F1", "accuracy", "TP", "FP", "FN", "TN"]}]),
                 hide_index=True)

    st.subheader("Configuración")
    st.json({"hiperparametros": metadatos["hiperparametros"], "particion": metadatos["particion"],
             "random_state": metadatos["random_state"],
             "tiempo_entrenamiento_s": metadatos["tiempo_entrenamiento_s"],
             "version_sklearn": metadatos["version_sklearn"]})

    # Tabla comparativa del notebook 02 (si ya se ejecutó). En el Avance 2 tendrá más filas.
    ruta_tabla = RAIZ / "docs" / "resultados_baseline_val.csv"
    if ruta_tabla.exists():
        st.subheader("Comparación con el baseline (validación)")
        st.dataframe(pd.read_csv(ruta_tabla).round(4), hide_index=True)
    ruta_pr = RAIZ / "docs" / "capturas" / "02_curva_pr_val.png"
    if ruta_pr.exists():
        st.image(str(ruta_pr), caption="Curva Precisión-Recall en validación", width=600)


# ------------------------------------------------------------------ Sección 3: Acerca del proyecto
def seccion_acerca():
    st.header("Acerca del proyecto")
    st.markdown("""
Proyecto semestral de **Inteligencia Artificial 2026-2**, Ingeniería Civil en Informática, Universidad del Bío-Bío.
Tema 12: *Detección de fraude en transacciones bancarias*.

**Equipo:** Daniel Canto · Diego Figueroa · Maximiliano Concha. **Docente:** Danelys Brito González.

**Qué hace el sistema:** asigna a cada transacción un *puntaje de riesgo* (probabilidad estimada de fraude) y permite
elegir el *umbral* a partir del cual se genera una alerta. Bajar el umbral detecta más fraudes (menos FN, dinero perdido)
a cambio de más falsas alarmas (más FP, clientes con el pago bloqueado).

**Datos:** Credit Card Fraud Detection, Machine Learning Group (ULB), Kaggle. Licencia ODbL.
Dal Pozzolo et al. (2015). 284.807 transacciones (283.726 sin duplicados), 0,167 % fraudes.
Las variables V1–V28 son componentes PCA anonimizados.

**Declaración ética:** los resultados son académicos y no constituyen una decisión sobre clientes reales.
""")


# ------------------------------------------------------------------ Enrutamiento del menú
if seccion == "Analizar transacciones":
    seccion_analizar()
elif seccion == "Resultados del modelo":
    seccion_resultados()
else:
    seccion_acerca()
