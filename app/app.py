"""
Sistema de Monitoreo y Detección de Fraude Bancario
Proyecto Semestral - Inteligencia Artificial 2026-2 (UBB)
Equipo: Daniel Canto · Diego Figueroa · Maximiliano Concha
"""
import json
import sys
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Ruta raíz para importar módulos de src/
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.config import COLUMNA_OBJETIVO, DIR_DATOS, DIR_MODELOS  # noqa: E402
from src.evaluacion import evaluar, graficar_curva_pr, graficar_matriz_confusion  # noqa: E402

MODELOS = {
    "Regresión logística (Baseline sin balanceo)": "logistica_sin_balanceo.joblib",
}
RUTA_EJEMPLO = DIR_DATOS / "ejemplo_transacciones.csv"

# ------------------------------------------------------------------ Funciones con caché
@st.cache_resource
def cargar_modelo(nombre_archivo: str):
    """Carga modelo y metadatos una sola vez en memoria."""
    return joblib.load(DIR_MODELOS / nombre_archivo)


@st.cache_data
def calcular_puntajes(nombre_archivo: str, X: pd.DataFrame):
    """Calcula las probabilidades de fraude y las almacena en caché."""
    modelo = cargar_modelo(nombre_archivo)["modelo"]
    return modelo.predict_proba(X)[:, 1]


def validar_columnas(df: pd.DataFrame, columnas_esperadas: list):
    """Verifica que el lote cumpla con el esquema requerido."""
    problemas = []
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        problemas.append(f"Faltan {len(faltantes)} columnas requeridas: {', '.join(faltantes[:5])}{'...' if len(faltantes) > 5 else ''}")
        return problemas
    no_numericas = [c for c in columnas_esperadas if not pd.api.types.is_numeric_dtype(df[c])]
    if no_numericas:
        problemas.append(f"Columnas con formato no numérico: {', '.join(no_numericas[:4])}")
    con_nulos = [c for c in columnas_esperadas if df[c].isna().any()]
    if con_nulos:
        problemas.append(f"Columnas con registros vacíos: {', '.join(con_nulos[:4])}")
    if COLUMNA_OBJETIVO in df.columns and not df[COLUMNA_OBJETIVO].isin([0, 1]).all():
        problemas.append(f"La columna {COLUMNA_OBJETIVO} debe contener exclusivamente 0 (legítima) o 1 (fraude).")
    return problemas


# ------------------------------------------------------------------ Configuración de la interfaz
st.set_page_config(
    page_title="Detección de fraude",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para aspecto institucional / fintech
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 10px;
    }
    .alerta-box {
        background-color: #fff3cd;
        border-radius: 6px;
        padding: 10px 14px;
        color: #856404;
        font-size: 0.9rem;
        margin-bottom: 15px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Barra lateral
with st.sidebar:
    st.markdown("### 🏦 Panel de Control")
    seccion = st.radio(
        "Navegación",
        ["Monitoreo de transacciones", "Desempeño del modelo", "Ficha técnica y ética"]
    )
    st.markdown("---")
    
    disponibles = {n: f for n, f in MODELOS.items() if (DIR_MODELOS / f).exists()}
    if not disponibles:
        st.error("⚠️ No se encontró el modelo entrenado. Ejecuta: `python -m src.entrenar_baseline`")
        st.stop()
    
    nombre_modelo = st.selectbox("Modelo", list(disponibles.keys()))
    archivo_modelo = disponibles[nombre_modelo]
    paquete_modelo = cargar_modelo(archivo_modelo)
    metadatos = paquete_modelo["metadatos"]
    validacion = paquete_modelo.get("validacion")
    
    st.caption(f"**Versión:** {metadatos.get('fecha_entrenamiento', 'Avance 1')[:10]}")


# ------------------------------------------------------------------ Sección 1: Monitoreo (Dashboard 2 columnas)
def seccion_analizar():
    st.markdown("## 💳 Detección de fraude en transacciones bancarias")
    
    # Barra de alerta ética compacta
    st.markdown(
        '<div class="alerta-box">⚠️ <b>Entorno Académico:</b> Las clasificaciones emitidas representan estimaciones estadísticas con fines de evaluación docente.</div>',
        unsafe_allow_html=True
    )

    # 1. Selector de fuente de datos (a la izquierda, check debajo de subir CSV)
    c_carga, _ = st.columns([1, 1])
    with c_carga:
        archivo = st.file_uploader("Subir archivo CSV con transacciones", type=["csv"])
        usar_ejemplo = st.checkbox("Usar lote de demostración (2.000 tx validadas)", value=False)

    if archivo is not None and not usar_ejemplo:
        df = pd.read_csv(archivo)
    elif usar_ejemplo and RUTA_EJEMPLO.exists():
        df = pd.read_csv(RUTA_EJEMPLO)
    else:
        st.info("👋 Para comenzar, sube un archivo CSV o marca la casilla del lote de demostración.")
        return

    # 2. Validación de estructura
    columnas = metadatos["columnas"]
    problemas = validar_columnas(df, columnas)
    if problemas:
        st.error("El formato del lote no coincide con el modelo:")
        for p in problemas:
            st.write(f"- {p}")
        return

    tiene_clase = COLUMNA_OBJETIVO in df.columns
    puntajes = calcular_puntajes(archivo_modelo, df[columnas])

    # ------------------ LAYOUT EN 2 COLUMNAS ------------------
    col_izq, col_der = st.columns([5, 6], gap="large")

    with col_izq:
        st.markdown("### ⚙️ Ajuste de Política de Riesgo")
        umbral = st.slider(
            "Umbral de decisión (Score de fraude mínimo para activar alerta)",
            min_value=0.01,
            max_value=0.99,
            value=float(metadatos["umbral_por_defecto"]),
            step=0.01,
            help="Un umbral bajo prioriza capturar más fraudes (mayor Recall) asumiendo más revisiones manuales."
        )
        
        alerta = puntajes >= umbral
        total_alertas = int(alerta.sum())
        total_aprobadas = int((~alerta).sum())
        tasa_alerta = (total_alertas / len(df)) * 100

        # Tarjetas de decisión
        k1, k2, k3 = st.columns(3)
        k1.metric("Transacciones", f"{len(df):,}".replace(",", "."))
        k2.metric("🚨 Bloqueadas / Alerta", f"{total_alertas:,}".replace(",", "."), delta=f"{tasa_alerta:.1f}% del lote", delta_color="inverse")
        k3.metric("✅ Aprobadas", f"{total_aprobadas:,}".replace(",", "."))

        # Métricas de efectividad si se dispone de etiquetas reales
        if tiene_clase:
            st.markdown("---")
            st.markdown("### 🎯 Métricas de Clasificación")
            res = evaluar(df[COLUMNA_OBJETIVO], puntajes, umbral=umbral)
            
            m1, m2 = st.columns(2)
            m1.metric("Precisión (Efectividad)", f"{res['precision']*100:.1f}%", help="Porcentaje de alertas que efectivamente resultaron ser fraude.")
            m2.metric("Recall (Cobertura)", f"{res['recall']*100:.1f}%", help="Porcentaje de fraudes totales capturados por el sistema.")

            tab_matriz, tab_comparativa = st.tabs(["Matriz de Confusión", "Comparativa Poblacional"])
            
            with tab_matriz:
                fig, ax = plt.subplots(figsize=(4, 3.2))
                graficar_matriz_confusion(res["matriz"], titulo=f"Matriz con umbral {umbral:.2f}", ax=ax)
                plt.tight_layout()
                st.pyplot(fig, use_container_width=False)
                plt.close(fig)
                st.caption(f"**AUPRC del modelo:** {res['AUPRC']:.3f} | **Aciertos:** {res['TP']} fraudes detectados y {res['TN']:,} legítimas aprobadas.".replace(",", "."))

            with tab_comparativa:
                if validacion is not None:
                    rv = evaluar(validacion["y"], validacion["puntaje"], umbral=umbral)
                    tabla_comp = pd.DataFrame([
                        {
                            "Población": f"Lote actual ({len(df):,} tx)",
                            "Fraudes Hallados (TP)": res["TP"],
                            "Falsas Alarmas (FP)": res["FP"],
                            "Precisión": f"{res['precision']*100:.1f}%",
                            "Recall": f"{res['recall']*100:.1f}%"
                        },
                        {
                            "Población": f"Validación Real ({len(validacion['y']):,} tx)",
                            "Fraudes Hallados (TP)": rv["TP"],
                            "Falsas Alarmas (FP)": rv["FP"],
                            "Precisión": f"{rv['precision']*100:.1f}%",
                            "Recall": f"{rv['recall']*100:.1f}%"
                        }
                    ])
                    st.dataframe(tabla_comp, hide_index=True)
                    st.caption("ℹ️ *Nota: El lote de muestra contiene una densidad sintética mayor de fraudes para probar la interfaz; la segunda fila proyecta el resultado real a escala de todo el banco.*")

    with col_der:
        st.markdown("### 📋 Bandeja de Operaciones Priorizadas")
        
        # Filtros rápidos para la tabla
        filtro_vista = st.radio(
            "Ver en bandeja:",
            ["Solo alertas sospechosas", "Todas las transacciones"],
            horizontal=True
        )

        df_operacion = df.copy()
        df_operacion["Score Riesgo"] = puntajes
        df_operacion["Dictamen"] = ["🚨 ALERTA" if a else "✅ Aprobada" for a in alerta]

        if filtro_vista == "Solo alertas sospechosas":
            df_mostrar = df_operacion[df_operacion["Score Riesgo"] >= umbral]
        else:
            df_mostrar = df_operacion

        # Ordenar por mayor riesgo primero
        df_mostrar = df_mostrar.sort_values(by="Score Riesgo", ascending=False)

        cols_mostrar = ["Dictamen", "Score Riesgo", "Amount", "Time"]
        if tiene_clase:
            cols_mostrar.append(COLUMNA_OBJETIVO)
        # Mostrar algunas variables PCA clave si existen
        for col_v in ["V17", "V14", "V12", "V4"]:
            if col_v in df_mostrar.columns:
                cols_mostrar.append(col_v)

        st.dataframe(
            df_mostrar[cols_mostrar],
            column_config={
                "Score Riesgo": st.column_config.ProgressColumn(
                    "Score",
                    help="Probabilidad calculada entre 0 y 1",
                    format="%.3f",
                    min_value=0.0,
                    max_value=1.0,
                ),
                "Amount": st.column_config.NumberColumn("Monto ($)", format="$%.2f"),
                "Time": st.column_config.NumberColumn("Segundos"),
                "Class": st.column_config.TextColumn("Real")
            },
            height=580,
            use_container_width=True
        )
        st.caption(f"Mostrando {len(df_mostrar):,} operaciones ordenadas por nivel de riesgo decreciente.".replace(",", "."))


# ------------------------------------------------------------------ Sección 2: Resultados del modelo
def seccion_resultados():
    st.markdown("## 📊 Evaluación Técnica y Comparativa de Modelos")
    st.write(f"**Arquitectura activa:** {metadatos['descripcion']}")

    tab1, tab2, tab3 = st.tabs(["Curva Precisión-Recall", "Análisis de Sensibilidad (Umbrales)", "Ficha de Entrenamiento"])

    with tab1:
        c_graf, c_info = st.columns([3, 2])
        with c_graf:
            if validacion is not None:
                fig, ax = plt.subplots(figsize=(6, 4))
                graficar_curva_pr(
                    validacion["y"],
                    {metadatos["descripcion"]: validacion["puntaje"]},
                    titulo="Curva PR — Conjunto de Validación",
                    ax=ax
                )
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
        with c_info:
            st.markdown("#### ¿Por qué la Curva PR?")
            st.write(
                "En escenarios donde el fraude representa menos del 0,2% del volumen total, la curva ROC suele ser engañosa "
                "por el enorme peso de los verdaderos negativos. La curva **Precisión-Recall** y su área bajo la curva (**AUPRC**) "
                "evalúan directamente la capacidad de rescatar transacciones fraudulentas sin inundar al equipo con falsas alarmas."
            )
            mv = metadatos["metricas_val"]
            st.metric("AUPRC Baseline", f"{mv['AUPRC']:.4f}")
            st.metric("Precisión (umbral 0.5)", f"{mv['precision']*100:.1f}%")
            st.metric("Recall (umbral 0.5)", f"{mv['recall']*100:.1f}%")

    with tab2:
        st.markdown("#### Desempeño según el Umbral Operativo")
        st.write("Evaluación proyectada sobre la totalidad del conjunto de validación (42.559 operaciones reales):")
        df_u = pd.DataFrame(metadatos["umbrales_val"])
        st.dataframe(
            df_u,
            column_config={
                "umbral": st.column_config.NumberColumn("Umbral", format="%.2f"),
                "precision": st.column_config.NumberColumn("Precisión", format="%.3f"),
                "recall": st.column_config.NumberColumn("Recall", format="%.3f")
            },
            hide_index=True
        )
        st.info("💡 **Observación:** Al descender el umbral de 0,5 a 0,1, la detección de fraudes (Recall) se incrementa de un 49% a casi un 72%, con un impacto controlado en falsas alarmas.")

    with tab3:
        st.markdown("#### Parámetros del Entorno")
        st.json({
            "Pipeline": metadatos["hiperparametros"],
            "Muestras de Entrenamiento": f"{metadatos['particion']['train']:,} transacciones ({metadatos['particion']['fraudes_train']} fraudes)",
            "Tiempo de Ajuste": f"{metadatos['tiempo_entrenamiento_s']} segundos",
            "Semilla Aleatoria": metadatos["random_state"]
        })


# ------------------------------------------------------------------ Sección 3: Acerca de
def seccion_acerca():
    st.markdown("## 🏛️ Contexto del Proyecto y Consideraciones Éticas")
    st.markdown("""
    **Asignatura:** Inteligencia Artificial (2026-2) — Universidad del Bío-Bío  
    **Docente:** Danelys Brito González  
    **Integrantes:** Daniel Canto · Diego Figueroa · Maximiliano Concha  

    ---
    ### 🛡️ Compromiso Ético y Uso Responsable
    1. **Entorno Académico:** El sistema ha sido concebido para el análisis técnico de algoritmos de clasificación ante severo desbalance de clases. No debe utilizarse para bloquear operaciones financieras reales sin supervisión humana.
    2. **Privacidad de Datos:** El dataset utilizado corresponde al benchmark internacional del *Machine Learning Group (ULB)*, donde las características personales se encuentran protegidas mediante transformaciones de Componentes Principales (PCA).
    3. **Impacto Operativo:** El diseño pone especial énfasis en el control de falsos positivos para evitar la discriminación o retención arbitraria de transacciones a clientes legítimos.
    """)


# Enrutamiento
if seccion == "Monitoreo de transacciones":
    seccion_analizar()
elif seccion == "Desempeño del modelo":
    seccion_resultados()
else:
    seccion_acerca()
