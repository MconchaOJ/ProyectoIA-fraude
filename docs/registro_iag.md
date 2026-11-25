# Registro de uso de IA generativa (Anexo IAG)

**Proyecto:** Detección de fraude en transacciones bancarias (Tema 12) — IA 2026-2, UBB.  
**Equipo:** Daniel Canto · Diego Figueroa · Maximiliano Concha.  
**Docente:** Danelys Brito González.

---

### Entrada 1 — Claude chat — Orientación inicial
- **Prompt (resumido):** Orientación sobre la pauta del proyecto semestral y temas sugeridos.
- **Respuesta / qué entregó:** Explicación general de las tres áreas del curso (AG, RNA, ML) y recomendación de abordar el Tema 12 (Detección de fraude) por contar con métricas bien definidas y datasets estándar en la industria.
- **Justificación del uso:** Apoyo inicial para lluvia de ideas y evaluación de factibilidad técnica del tema.
- **Verificación hecha por el equipo:** Se revisó la pauta general del curso en Moodle, confirmando que el tema 12 estaba disponible y cumplía con las restricciones de técnicas clásicas requeridas.
- **Análisis crítico:** La sugerencia inicial fue adecuada pero genérica; no consideraba la dificultad práctica de manipular datasets con más de 200.000 filas en equipos personales.
- **Qué modificó o decidió el equipo:** El equipo eligió formalmente el Tema 12 y definió centrar el trabajo en el severo desbalance de clases.

---

### Entrada 2 — Claude chat — Plan por entregas
- **Prompt (resumido):** Plan de trabajo por entregas y cronograma según las fechas del semestre.
- **Respuesta / qué entregó:** Desglose por hitos (Propuesta, Avance 1, Avance 2, Entrega Final) con entregables técnicos recomendados para cada etapa.
- **Justificación del uso:** Planificación y gestión del tiempo de desarrollo grupal.
- **Verificación hecha por el equipo:** Se contrastó fecha por fecha contra la tabla oficial del cronograma de la asignatura (octubre a diciembre de 2026).
- **Análisis crítico:** La IA propuso probar redes neuronales complejas en fases tempranas, lo cual se alejaba de la indicación del curso que exigía baselines lineales primero.
- **Qué modificó o decidió el equipo:** Se ajustó el Avance 1 para incluir únicamente los baselines obligatorios (Dummy y Regresión Logística), postergando modelos avanzados para el Avance 2.

---

### Entrada 3 — Claude chat — Material de clases y dataset
- **Prompt (resumido):** Envío de los 12 PDF de clases de la asignatura y consulta sobre qué dataset público utilizar.
- **Respuesta / qué entregó:** Recomendación del benchmark *Credit Card Fraud Detection* de Kaggle (ULB, 2015). Notificó además que técnicas clave para fraude (AUPRC, SMOTE, Isolation Forest) aún no se habían cubierto en la materia dictada.
- **Justificación del uso:** Búsqueda y selección de fuentes de datos confiables y con licencias abiertas.
- **Verificación hecha por el equipo:** Se ingresó directamente a Kaggle, comprobando la licencia Open Database License (ODbL), los autores (Andrea Dal Pozzolo et al.) y que el dataset tuviera los 492 fraudes declarados sin valores nulos.
- **Análisis crítico:** Muy acertada la advertencia conceptual: evidenció que el equipo debía autoformarse en evaluación de clases desbalanceadas (AUPRC) fuera del temario estándar de clases.
- **Qué modificó o decidió el equipo:** Se adoptó oficialmente el dataset de ULB y se descartaron datasets sintéticos (como PaySim) para trabajar con fraude bancario real.

---

### Entrada 4 — Claude chat — Borrador de la propuesta
- **Prompt (resumido):** Apoyo en la redacción preliminar del documento formal de la propuesta (máximo 3 páginas).
- **Respuesta / qué entregó:** Estructura en secciones: planteamiento, objetivos general y específicos, marco técnico (PEAS), cálculo bayesiano de falsas alarmas y boceto de interfaz.
- **Justificación del uso:** Redacción técnica y síntesis formal de objetivos conforme al estándar institucional UBB.
- **Verificación hecha por el equipo:** Se comprobó matemáticamente el cálculo de probabilidad condicional con el Teorema de Bayes formulado en la propuesta: $P(\text{fraude}|\text{alerta}) \approx 13\%$.
- **Análisis crítico:** El borrador redactado por la IA utilizaba términos excesivamente comerciales. Hubo que aterrizar los objetivos a términos de ingeniería medibles (superar baseline en AUPRC sobre conjunto de prueba).
- **Qué modificó o decidió el equipo:** El equipo reescribió los objetivos específicos (OE1 y OE2) y diseñó el wireframe funcional de la aplicación Streamlit.

---

### Entrada 5 — 2026-11-07 — Claude chat
- **Prompt (resumido):** Revisión de los requisitos específicos del Avance 1 y generación del archivo de directrices de desarrollo `CLAUDE.md`.
- **Respuesta / qué entregó:** Checklist exhaustivo del Avance 1 y archivo `CLAUDE.md` con reglas de diseño (fuga de datos, partición 70/15/15, reproducibilidad, no usar accuracy).
- **Justificación del uso:** Establecer directrices de codificación estrictas para evitar errores metodológicos en machine learning.
- **Verificación hecha por el equipo:** Se validó que las restricciones coincidieran con la pauta de evaluación del Avance 1.
- **Análisis crítico:** Útil para fijar estándares; sin embargo, requirió supervisión humana para evitar que la IA intentara implementar de golpe librerías no solicitadas.
- **Qué modificó o decidió el equipo:** Se fijó la semilla aleatoria en 42 y se estipuló que el conjunto de prueba queda estrictamente congelado hasta el informe final.

---

### Entrada 6 — 2026-11-07 — Claude Code
- **Prompt (resumido):** Generar la arquitectura base de carpetas modulares (`src/`, `data/`, `models/`, `notebooks/`, `docs/`, `app/`) y script de configuración.
- **Respuesta / qué entregó:** Repositorio estructurado, `.gitignore` adecuado a datos pesados, `src/config.py` con constantes centralizadas y `src/descargar_datos.py`.
- **Justificación del uso:** Apoyo técnico para garantizar una estructura de proyecto profesional y reproducible.
- **Verificación hecha por el equipo:** Se ejecutó `python -m src.descargar_datos` en terminal local, verificando la descarga íntegra de `creditcard.csv` (150 MB).
- **Análisis crítico:** La estructura inicial propuesta incluía subcarpetas redundantes.
- **Qué modificó o decidió el equipo:** Se consolidó el directorio raíz directo sin anidaciones innecesarias, asegurando que las importaciones relativas de Python funcionaran sin conflictos de `sys.path`.

---

### Entrada 7 — 2026-11-07 — Claude Code
- **Prompt (resumido):** Fijar dependencias en `requirements.txt`, auditar el dataset descargado y generar la documentación del `README.md`.
- **Respuesta / qué entregó:** Archivo `requirements.txt` con versiones congeladas (scikit-learn 1.9.1, pandas, streamlit, etc.), conteo de registros y borrador de `README.md`.
- **Justificación del uso:** Garantizar la reproducibilidad estricta del entorno en cualquier computador del equipo.
- **Verificación hecha por el equipo:** Se recreó el entorno `.venv` desde cero mediante `pip install -r requirements.txt`, verificando que todas las librerías compilaran sin errores en Windows 11.
- **Análisis crítico:** La IA detectó 1.081 filas repetidas en el CSV pero no profundizó en su causa ni en cómo afectaban al modelado.
- **Qué modificó o decidió el equipo:** El equipo debatió el impacto de los duplicados: al contener exactamente los mismos valores en las 30 variables continuas, mantenerlos en conjuntos distintos equivaldría a fuga de datos (data leakage). Se instruyó eliminarlos antes de particionar.

---

### Entrada 8 — 2026-11-07 — Claude Code
- **Prompt (resumido):** Implementar la función de eliminación de duplicados en `src/datos.py` y crear el notebook `notebooks/01_exploracion.ipynb`.
- **Respuesta / qué entregó:** Código modular con `eliminar_duplicados()` (reportando distribución por clase) y notebook estructurado en 8 secciones de análisis exploratorio.
- **Justificación del uso:** Acelerar el código de visualización gráfica (histogramas KDE, escala logarítmica y correlación lineal).
- **Verificación hecha por el equipo:** Se comprobó empíricamente el conteo: 1.081 duplicados eliminados (1.062 legítimas y 19 fraudes), resultando en 283.726 transacciones y 473 fraudes (0,167 %).
- **Análisis crítico:** La IA inicialmente insinuaba que los duplicados eran "errores de base de datos". El equipo reconoció que en la vida real podrían ser transacciones repetidas legítimas (ej. doble cobro), pero que metodológicamente debían quitarse por precaución ante sobreajuste en validación.
- **Qué modificó o decidió el equipo:** Se dejó la eliminación de duplicados activa por defecto en `cargar_datos()`, y se dejaron las celdas de interpretación en blanco para que Daniel analizara los resultados personalmente.

---

### Entrada 9 — 2026-11-07 — Claude Code
- **Prompt (resumido):** Crear `src/evaluacion.py`, `src/modelos.py` y el notebook `notebooks/02_baseline.ipynb` con evaluación estratificada 70/15/15.
- **Respuesta / qué entregó:** Pipeline con `StandardScaler` y `LogisticRegression(solver='lbfgs', C=1.0, max_iter=1000)`; funciones para matriz de confusión y curva PR con línea base del azar; evaluación en validación.
- **Justificación del uso:** Implementación del pipeline de scikit-learn y curvas de desempeño para clases severamente desbalanceadas.
- **Verificación hecha por el equipo:** Se verificó que la estratificación mantuviera el 0,167 % de fraudes en los tres conjuntos (331 en Train, 71 en Val, 71 en Test) y se calculó a mano un ejemplo de confusión con matriz 2×2 para comprobar la exactitud de `evaluar()`.
- **Análisis crítico:** La IA pretendía evaluar inicialmente con métrica ROC-AUC. El equipo insistió en AUPRC como métrica rectora, demostrando con el notebook que la línea del azar en AUPRC es la prevalencia real (0,0017), lo que ilustra con fidelidad el verdadero aporte del modelo.
- **Qué modificó o decidió el equipo:** Se integró el escalador dentro del Pipeline para evitar fuga de información desde validación/test hacia el ajuste de medias.

---

### Entrada 10 — 2026-11-07 — Claude Code
- **Prompt (resumido):** Crear script de serialización `src/entrenar_baseline.py`, generador de lote de prueba `src/crear_csv_ejemplo.py` y primera versión de `app/app.py` en Streamlit.
- **Respuesta / qué entregó:** Guardado de modelo en formato `.joblib` junto a metadatos `.json`, subconjunto de prueba `data/ejemplo_transacciones.csv` e interfaz web interactiva.
- **Justificación del uso:** Conexión del modelo con la interfaz gráfica requerida en el Objetivo Específico 2 (OE2).
- **Verificación hecha por el equipo:** Maximiliano ejecutó la app localmente, probó el slider de umbral y verificó que el modelo respondiera en tiempo real gracias al decorador `@st.cache_resource`.
- **Análisis crítico:** Se detectó un sesgo grave en la demo: al construir el CSV de ejemplo con 71 fraudes y solo 1.929 legítimas (3,55 % de fraudes), la precisión en la app se mostraba artificialmente en 98-100%, ocultando las falsas alarmas reales.
- **Qué modificó o decidió el equipo:** El equipo exigió incorporar una comparativa poblacional en vivo dentro de la app que contraste las métricas del lote de muestra contra las 42.559 transacciones de validación completa.

---

### Entrada 11 — 2026-11-07 — Claude Code
- **Prompt (resumido):** Documentar los flujos del sistema en Mermaid (`docs/diagrama_flujo.md`) y unificar la definición del pipeline en `src/modelos.py`.
- **Respuesta / qué entregó:** Diagrama de entrenamiento fuera de línea y diagrama de uso en Streamlit, junto a tablas explicativas por bloque.
- **Justificación del uso:** Documentación visual de la arquitectura del software.
- **Verificación hecha por el equipo:** Se cargaron los bloques Mermaid en mermaid.live para verificar la ausencia de errores sintácticos.
- **Análisis crítico:** Los diagramas generados contenían demasiado texto explicativo dentro de cada nodo, dificultando su lectura en láminas de presentación.
- **Qué modificó o decidió el equipo:** Se simplificaron las etiquetas de los nodos para facilitar su comprensión visual.

---

### Entrada 12 — 2026-11-07 — Claude Code
- **Prompt (resumido):** Elaborar guía de estudio y banco de preguntas (`docs/guia_estudio.md`) para preparar la defensa oral individual.
- **Respuesta / qué entregó:** 25 preguntas frecuentes distribuidas por temática e integrante, glosario técnico y desglose cuantitativo de los resultados del repositorio.
- **Justificación del uso:** Preparación estratégica para las preguntas individuales de la defensa oral (evaluadas individualmente según rúbrica).
- **Verificación hecha por el equipo:** Cada integrante estudió las preguntas asignadas a su área (Daniel: datos; Diego: modelo y métricas; Maximiliano: interfaz).
- **Análisis crítico:** Toda afirmación matemática (ej. la relación entre el Teorema de Bayes y la precisión) fue comprobada numéricamente con los datos de validación.
- **Qué modificó o decidió el equipo:** Se adoptó la guía como material de consulta interna del grupo.

---

### Entrada 13 — 2026-11-13 — Claude Code / Asistente Antigravity
- **Prompt (resumido):** Asistencia en la ejecución local del proyecto en IntelliJ/PowerShell, rediseño ergonómico de la interfaz Streamlit y finalización de entregables del Avance 1.
- **Respuesta / qué entregó:** Configuración de entorno Python 3.14 local, ejecución y guardado de celdas en `01_exploracion.ipynb` y `02_baseline.ipynb`, rediseño de `app/app.py` en 2 columnas con bandeja en tiempo real y barras de riesgo, y exportación de diagramas a PNG.
- **Justificación del uso:** Apoyo técnico en despliegue local, depuración de interfaces de usuario y generación de evidencia visual para el informe.
- **Verificación hecha por el equipo:** Daniel ejecutó los notebooks directamente en Jupyter Notebook local observando las salidas y figuras guardadas en disco. Se probó la app en el navegador web local, verificando el comportamiento del slider de umbral y la visualización de la matriz de confusión.
- **Análisis crítico:** La interfaz Streamlit inicial generaba un scroll vertical excesivo que no permitía comparar el umbral con las transacciones. El equipo rediseñó el layout a dos columnas y eliminó textos con tono de plantilla de IA para dotarla de un enfoque bancario profesional.
- **Qué modificó o decidió el equipo:** Se sustituyó el título y la estructura visual de la app; se desmarcó el lote de prueba por defecto para permitir al usuario elegir la fuente de datos; se exportaron los diagramas a formato PNG para el informe académico y se eliminaron capturas obsoletas del repositorio.

---

### Entrada 14 — 2026-11-21 — Claude Code / Asistente Antigravity (Avance 2: Modelado Comparativo y Anti-Fuga)
- **Prompt (resumido):** Implementar las técnicas de manejo de desbalance (`class_weight='balanced'` y SMOTE), Random Forest e Isolation Forest en `src/modelos.py`, `src/entrenar_modelos.py` y `notebooks/03_modelos.ipynb`, comparando contra el baseline del Avance 1.
- **Respuesta / qué entregó:** Cuatro nuevos pipelines unificados (`crear_logistica_balanceada`, `crear_logistica_smote`, `crear_random_forest`, `crear_isolation_forest`), adaptador `IsolationForestWrapper` para normalizar `-score_samples` a probabilidades en `[0, 1]`, tabla comparativa de validación (`docs/resultados_modelos_val.csv`) y curvas Precisión-Recall superpuestas.
- **Justificación del uso:** Acelerar la escritura de pipelines reproducibles con `imblearn.pipeline.Pipeline` y automatizar el benchmark de los 5 modelos bajo la misma partición estratificada.
- **Verificación hecha por el equipo:** Ejecución completa local de `python -m src.entrenar_modelos` verificando métricas en validación (`42.559` transacciones, `71` fraudes) y comprobando que `X_test` e `y_test` permanecieran sellados y sin evaluar.
- **Análisis crítico (sesgos y errores detectados en la IAG):** La IA propuso inicialmente entrenar Random Forest con `n_estimators=500` y `max_depth=None` (sin límite de profundidad) y llegó a sugerir mostrar ROC-AUC como métrica secundaria destacada.
- **Qué modificó o decidió el equipo:** El equipo rechazó esa parametrización para evitar sobreajuste (*overfitting*) sobre los 331 fraudes de entrenamiento y tiempos altos de cómputo, podando a **`max_depth=12` y `100` árboles** (logrando AUPRC `0,8280` en `28,94 s`); rechazó ROC-AUC manteniendo **AUPRC** como métrica rectora; y auditó que SMOTE estuviera encapsulado dentro de `ImbPipeline` aprendiendo exclusivamente en `Train`.

---

### Entrada 15 — 2026-11-22 — Asistente Antigravity (Avance 2: Streamlit Multi-Modelo e Informe Técnico)
- **Prompt (resumido):** Actualizar la interfaz `app/app.py` con selector dinámico para los 5 modelos, depurar errores al cambiar entre modelos y estructurar el informe técnico del Avance 2 respetando el máximo de 5 páginas.
- **Respuesta / qué entregó:** Selector multi-modelo en la barra lateral, corrección de accesos inseguros en metadatos JSON (`KeyError` en `umbral_por_defecto` e `hiperparametros`, `NameError` en `modelo_id`), mejora del caché de doble nivel (`@st.cache_resource` y `@st.cache_data`) y borrador del informe técnico `informe/Avance2_Deteccion_Fraude_UBB.pdf`.
- **Justificación del uso:** Depuración rápida de integración entre los binarios `.joblib` y Streamlit, y apoyo en maquetación técnica del informe manteniendo consistencia visual con el Avance 1.
- **Verificación hecha por el equipo:** Prueba local en navegador (`streamlit run app/app.py`) alternando en vivo entre los 5 modelos sobre `ejemplo_transacciones.csv` (`2.000` filas) y verificando las métricas reales contra las `42.559` transacciones completas de validación; verificación manual del conteo de páginas exacto del informe (`5 páginas`).
- **Análisis crítico:** Al probar la demo, el equipo corroboró que la precisión mostrada (`100 %` en lote demo vs `86,7 %` en validación completa) requiere explicación explícita por la prevalencia concentrada (`3,55 %` vs `0,167 %`), manteniendo la pestaña *Comparativa Poblacional* en el dashboard. Asimismo, en el análisis crítico del informe se constató que con solo `71` fraudes en validación los resultados deben tratarse como preliminares hasta abrir `Test` en diciembre.
- **Qué modificó o decidió el equipo:** Se añadieron valores por defecto seguros en la lectura de metadatos de `app/app.py`, se verificaron todas las cifras directamente desde `docs/resultados_modelos_val.csv` y `models/*.json`, y se editó la redacción del informe para reflejar con rigor técnico los límites de `class_weight`, SMOTE e Isolation Forest.

---

### Entrada 16 — 2026-11-25 — Asistente Antigravity (Avance 2: Cierre de Entregables y Guión Explicativo)
- **Prompt (resumido):** Preparación de guión oral enfocado en explicar intuitivamente el umbral de decisión (`0,5`), revisión de compatibilidad de `README.md` y consolidación del repositorio para entrega en Moodle.
- **Respuesta / qué entregó:** Guía de explicación intuitiva del funcionamiento interno de los modelos y del umbral de corte, actualización de requisitos de Python en `README.md`, enlace al video demostrativo y limpieza final del repositorio.
- **Justificación del uso:** Estructurar la comunicación técnica del equipo para la defensa oral individual (máx. 5 minutos) y validar la reproducibilidad de instalación.
- **Verificación hecha por el equipo:** Al intentar instalar en otro equipo con Python 3.10 fallaron las dependencias fijadas (`numpy 2.5.4`, `pandas 3.1.1`, `scikit-learn 1.9.1`); se comprobó que el entorno validado corre en **Python 3.14.6**, actualizando el `README.md`. También se probó la exportación de validación completa vs lote demo en la app y se grabó el video demostrativo en vivo.
- **Análisis crítico:** Se comprobó que la IA tiende a redactar guiones densos en cifras sin explicar el mecanismo intuitivo detrás del umbral; el equipo reenfocó el discurso hacia la interpretación causal (score continuo vs línea de corte).
- **Qué modificó o decidió el equipo:** Se dejó explícita en `README.md` la compatibilidad real (Python 3.14) y el enlace público al video de demostración.

---

### Reflexión Intermedia sobre el Uso de IAG (Anexo Parcial — Avance 2)
- **Cómo contribuyó:** Aceleró la estructuración modular del código (`src/modelos.py`, `src/entrenar_modelos.py`), la implementación de gráficas comparativas PR y la depuración de errores de integración en Streamlit, liberando tiempo al equipo para el análisis experimental y la preparación de la defensa oral.
- **Limitaciones y sesgos observados:** (1) Tendencia de los modelos generativos a proponer arquitecturas sobreajustadas (`max_depth=None`, `500` árboles) o métricas inadecuadas para desbalance extremo (`ROC-AUC`, `accuracy`) si no se les imponen restricciones explícitas; (2) inconsistencias ocasionales entre nombres de claves en metadatos JSON y el código consumidor de la app (`KeyError` / `NameError` detectados al ejecutar en local); (3) desfase entre la versión de Python documentada inicialmente (`3.10`) y las versiones reales soportadas por los paquetes congelados (`3.14.6`).
- **Criterio humano aplicado:** Ningún resultado ni hiperparámetro fue aceptado sin verificación empírica local sobre la partición estratificada con semilla `42`, manteniendo el conjunto de prueba (`Test`) completamente sellado para la evaluación final.
