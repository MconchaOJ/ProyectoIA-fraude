# Guía de estudio — Defensa del proyecto (Avance 1)

**Proyecto:** Detección de fraude en transacciones bancarias (Tema 12) — IA 2026-2, UBB
**Equipo:** Daniel Canto (datos y baseline) · Diego Figueroa (modelos, desbalance y métricas) · Maximiliano Concha (interfaz e integración)
**Estado al:** 2026-11-07

> Todos los números de esta guía salen de ejecutar el código del repo: `src/entrenar_baseline.py`, `models/logistica_sin_balanceo.json`
> y ejecuciones de prueba de los notebooks. Cuando algo **no está hecho todavía**, se indica con ⏳.
> Los notebooks todavía **no tienen salidas guardadas** (el equipo debe ejecutarlos) y sus secciones de interpretación siguen como TODO.

---

## 1. El proyecto en 1 minuto

**Problema.** El fraude con tarjeta es muy poco frecuente. En nuestro dataset, después de quitar duplicados, hay **473 fraudes en
283.726 transacciones (0,167 %)**: 1 fraude por cada ~599 legítimas. Un fraude no detectado (falso negativo) es dinero perdido.
Una falsa alarma (falso positivo) es un cliente con su pago bloqueado.

**Por qué la accuracy engaña.** Un "modelo" que **nunca** alerta acierta el **99,83 %** de las transacciones de validación y no
detecta **ningún** fraude (recall 0). La accuracy queda dominada por la clase mayoritaria. Por eso usamos **AUPRC**,
**precisión** y **recall**, que se fijan en la clase fraude.

**Qué hace el sistema.** Un modelo de aprendizaje automático asigna a cada transacción un **puntaje de riesgo** (la probabilidad
estimada de fraude, entre 0 y 1). El usuario elige un **umbral**: si el puntaje es mayor o igual al umbral, se **alerta**; si no,
se **aprueba**. La interfaz en Streamlit permite mover el umbral y ver en vivo cuántos fraudes se detectan y cuántas falsas alarmas
se generan.

**Estado actual (Avance 1).**
- ✅ Datos descargados y verificados, duplicados eliminados, partición estratificada 70/15/15.
- ✅ Dos baselines evaluados en validación: Dummy «nunca fraude» (AUPRC 0,0017) y regresión logística sin balanceo (**AUPRC 0,688**).
- ✅ Modelo guardado con `joblib` y una interfaz Streamlit en borrador que funciona.
- ✅ Diagrama de flujo en Mermaid (`docs/diagrama_flujo.md`).
- ⏳ Falta que el equipo ejecute los notebooks y escriba sus interpretaciones. También faltan exportar el diagrama a PNG, tomar las capturas de la app, el PDF y las láminas.
- ⏳ Avance 2: `class_weight`, SMOTE, Random Forest, Isolation Forest (y Naive Bayes) **todavía no están implementados**.

---

## 2. Recorrido por el flujo, paso a paso

El diagrama completo está en `docs/diagrama_flujo.md`. Hay un flujo de **entrenamiento** (fuera de línea) y uno de **uso** (la interfaz).

### Paso 1 — Datos
- **Qué se hace:** se descarga `creditcard.csv` (Kaggle, Machine Learning Group de la ULB, licencia ODbL, Dal Pozzolo et al., 2015):
  284.807 transacciones y 31 columnas (`Time`, `V1`–`V28`, `Amount`, `Class`). No tiene valores nulos.
- **Por qué así:** es un dataset real, público y muy usado. Además trae justo el desbalance que queremos estudiar.
- **Alternativa:** datasets sintéticos de fraude (por ejemplo, simulados). Los descartamos porque preferimos datos reales.
- **Dónde:** `src/descargar_datos.py` → `descargar()` (usa `kagglehub`). El CSV **no** se sube al repositorio porque pesa ~150 MB.

### Paso 2 — Eliminar duplicados
- **Qué se hace:** se quitan las **1.081 filas** idénticas a otra en las 31 columnas (1.062 legítimas y 19 fraudes). Se conserva la primera aparición.
- **Por qué así:** si una fila queda en entrenamiento y su copia en validación o prueba, el modelo se evalúa con algo que
  ya vio (**fuga de información**) y las métricas salen infladas. Por eso se eliminan **antes** de partir.
- **Alternativa:** dejarlos, porque podrían ser transacciones reales repetidas (por ejemplo, un doble cobro), o eliminarlos
  después de partir, pero eso no evita que una copia quede en cada conjunto.
- **Dónde:** `src/datos.py` → `eliminar_duplicados()`. `cargar_datos()` la aplica por defecto, así que el baseline, los modelos y la
  app usan las mismas 283.726 filas.

### Paso 3 — Partición estratificada 70/15/15
- **Qué se hace:** se divide en entrenamiento (70 %), validación (15 %) y prueba (15 %), con `stratify=y` y semilla 42.
  Se hace en dos pasos: primero 70/30 y después el 30 % en mitades (`test_size=0,50`).
- **Por qué así:** `train_test_split` solo divide en dos partes. La estratificación mantiene ≈ 0,167 % de fraudes en los tres
  conjuntos. Sin ella, con tan pocos fraudes, un conjunto podría quedar con muchos menos. La semilla fija hace que la
  partición sea reproducible.
- **Alternativa:** partición **temporal** (entrenar con las primeras horas y evaluar con las últimas), más realista para
  producción; o **validación cruzada** estratificada. La propuesta comprometió 70/15/15 estratificada.
- **Dónde:** `src/datos.py` → `particionar()` y `tabla_particion()`. Las proporciones y la semilla están en `src/config.py`.

### Paso 4 — Pipeline (escalado + modelo)
- **Qué se hace:** `Pipeline([StandardScaler, LogisticRegression(solver="lbfgs", C=1.0, max_iter=1000)])`, **sin** manejo del desbalance.
  Se entrena **solo** con entrenamiento.
- **Por qué así:** el escalador va **dentro** del pipeline para que su media y desviación se calculen solo con entrenamiento
  (evita fuga de información). La regresión logística es lineal, rápida e interpretable, y entrega una probabilidad. Sin balanceo,
  sirve de referencia para medir si `class_weight` y SMOTE ayudan en el Avance 2.
- **Alternativa:** escalar todo el dataset antes de partir (incorrecto: produce fuga). Usar directamente un modelo más
  complejo sin baseline (no sabríamos si mejora algo).
- **Dónde:** `src/modelos.py` → `crear_logistica_sin_balanceo()`. Es **la única definición**: la usan el notebook 02 y el script de entrenamiento.

### Paso 5 — Evaluación en validación
- **Qué se hace:** se calcula AUPRC (métrica principal), precisión, recall, F1, accuracy (solo para contrastar) y la matriz de confusión,
  con umbral 0,5. Se compara con el Dummy «nunca fraude» y con el azar.
- **Por qué así:** con el desbalance, la accuracy no sirve. La AUPRC mide qué tan bien el puntaje ordena los fraudes arriba, sin
  depender del umbral. **La prueba no se toca:** se usa una sola vez, al final.
- **Alternativa:** AUC-ROC. Se descartó como métrica principal porque con tantas legítimas se ve optimista (ver sección 3).
- **Dónde:** `src/evaluacion.py` → `evaluar()`, `graficar_curva_pr()`, `graficar_matriz_confusion()`. Se usa en `notebooks/02_baseline.ipynb`.

### Paso 6 — Modelo guardado
- **Qué se hace:** `python -m src.entrenar_baseline` entrena y guarda `models/logistica_sin_balanceo.joblib`, que contiene el pipeline,
  los metadatos y los puntajes de validación. Guarda también `models/logistica_sin_balanceo.json` con los metadatos en texto.
- **Por qué así:** la interfaz carga el modelo ya entrenado y no reentrena. Un script permite regenerarlo con un solo comando,
  sin depender del estado de un notebook. Los metadatos dicen qué columnas espera el modelo, sus hiperparámetros y sus métricas.
- **Alternativa:** `pickle` directo (joblib es lo recomendado por scikit-learn para objetos con arreglos grandes); entrenar dentro
  de la app (lento y no reproducible).
- **Dónde:** `src/entrenar_baseline.py` → `entrenar_y_guardar()`, `tabla_umbrales()`.

### Paso 7 — Interfaz
- **Qué se hace:** la app recibe un CSV (o el de ejemplo), valida columnas, calcula puntajes y aplica el umbral del slider.
  Muestra alertas, métricas si hay `Class`, la matriz de confusión y la tabla ordenada por riesgo.
- **Por qué así:** cumple el OE2 de la propuesta: el usuario elige el equilibrio entre falsos negativos y falsos positivos.
- **Alternativa:** una interfaz con Flask o Tkinter (más trabajo), o un umbral fijo sin interacción (no permitiría ver el equilibrio entre ambos errores).
- **Dónde:** `app/app.py`. Se ejecuta con `streamlit run app/app.py`.

---

## 3. Conceptos clave (con nuestros números)

### Desbalance de clases
Una clase es muchísimo más frecuente que la otra. Aquí: 283.253 legítimas frente a 473 fraudes (0,167 %). **Consecuencia:** un modelo que
minimiza el error promedio aprende que decir "legítima" casi siempre sale barato.

### Matriz de confusión (TP, FP, FN, TN)
Tabla 2×2 que cruza la clase real con la predicción. Fraude = clase **positiva**.

|  | Predice legítima | Predice fraude |
|---|---|---|
| **Es legítima** | TN (verdadero negativo) | FP (falsa alarma) |
| **Es fraude** | FN (fraude que se escapa) | TP (fraude detectado) |

**Ejemplo (regresión logística, validación, umbral 0,5):** TP = 35, FP = 7, FN = 36, TN = 42.481.

### Precisión
**De las alertas, ¿cuántas eran fraude?** Precisión = TP / (TP + FP) = 35 / (35 + 7) = **0,833**. Cuando el modelo alerta, acierta el 83 % de las veces.

### Recall (sensibilidad)
**De los fraudes reales, ¿cuántos detectamos?** Recall = TP / (TP + FN) = 35 / (35 + 36) = **0,493**. Se escapa la mitad de los fraudes.

### F1
Media armónica de precisión y recall: F1 = 2·P·R / (P + R) = 2·0,833·0,493 / (0,833 + 0,493) = **0,620**. Si una de las dos es baja, F1 es baja.

### Accuracy (y por qué engaña)
(TP + TN) / total. El Dummy obtiene **0,9983** con recall 0. La regresión logística obtiene **0,9990**. Ambas parecen "casi perfectas",
pero una no detecta nada y la otra detecta la mitad. La accuracy no distingue entre ellas.

### Umbral de decisión
El modelo entrega un puntaje entre 0 y 1. El umbral lo convierte en decisión: **alerta si puntaje ≥ umbral**.
- **Umbral más bajo:** más alertas, por lo que sube el recall (menos fraudes se escapan), pero suben las falsas alarmas.
- **Umbral más alto:** menos alertas, más precisas, pero se escapan más fraudes.

0,5 es solo el valor por defecto de `predict()`; no tiene nada de especial para este problema. Ver la tabla de umbrales en la sección 4.

### Curva Precisión-Recall y AUPRC
Cada umbral da un par (recall, precisión). Al recorrer todos los umbrales se obtiene la **curva PR**. La **AUPRC** es el área bajo
esa curva (en scikit-learn, `average_precision_score`). Resume el desempeño **para todos los umbrales**, por eso no depende del umbral elegido.
Nuestra regresión logística: **0,688**.

**¿Por qué la AUPRC del azar es igual a la proporción de fraudes?** Un clasificador aleatorio pone puntajes sin relación con la clase.
Entonces, con cualquier umbral, las transacciones que alerta son una muestra al azar y tienen la misma proporción de fraudes que el
total (≈ 0,00167). Su precisión es ≈ 0,00167 para todo recall: la curva es una línea horizontal y su área es ≈ **0,00167**.
Lo comprobamos en el notebook 02: con puntajes al azar, la AUPRC dio **0,00163**, frente a una proporción de **0,00167**. El Dummy da lo mismo
(0,0017), porque pone el mismo puntaje (0) a todas las transacciones.

**¿Por qué no AUC-ROC?** La curva ROC usa la tasa de falsos positivos, FP / (FP + TN). Con 42.488 legítimas en validación, incluso 100 falsas
alarmas son una tasa de 0,2 %, y la curva se ve casi perfecta. La precisión, TP / (TP + FP), sí "siente" esas falsas alarmas. Además, en ROC
el azar vale 0,5; en PR vale 0,0017, lo que deja claro cuánto aporta el modelo.

### Estratificación
Partir los datos manteniendo la proporción de cada clase en cada conjunto. Resultado: 0,1667 % de fraudes en entrenamiento y 0,1668 % en validación y en prueba.

### Fuga de información (data leakage)
Que información de validación o prueba llegue al entrenamiento, aunque sea indirectamente. Hace que las métricas salgan mejores de lo que
serán con datos nuevos. Ejemplos que evitamos:
- (1) duplicados repartidos entre conjuntos;
- (2) escalar con la media de todo el dataset;
- (3) aplicar SMOTE antes de partir (Avance 2);
- (4) elegir el modelo o el umbral mirando la prueba.

### Por qué el escalado va dentro del pipeline
`StandardScaler` resta la media y divide por la desviación estándar. Si se ajusta con todo el dataset, la media "conoce" los datos
de validación y prueba (fuga). Dentro del `Pipeline`, `fit()` lo ajusta **solo con entrenamiento** y `predict_proba()` reutiliza esa
media y esa desviación. Es necesario porque `Amount` (hasta 25.691) y `Time` (hasta 172.792 s) están en escalas muy distintas a V1–V28.
Esa diferencia afecta a la regularización y a la convergencia del optimizador.

### Regresión logística
Calcula una combinación lineal z = w₀ + w₁x₁ + … + w₃₀x₃₀ y la pasa por la **sigmoide** σ(z) = 1 / (1 + e⁻ᶻ). El resultado es una
probabilidad entre 0 y 1, nuestro puntaje de riesgo. Los pesos wᵢ se aprenden minimizando la pérdida logarítmica (log-loss). A pesar
del nombre, es un **clasificador**. Es lineal: separa las clases con un hiperplano.

| Hiperparámetro | Nuestro valor | Qué hace |
|---|---|---|
| `solver` | `lbfgs` (por defecto) | Algoritmo de optimización (cuasi-Newton) que encuentra los pesos. Es determinista: siempre da el mismo resultado. |
| `C` | 1,0 (por defecto) | **Inverso** de la fuerza de regularización L2, que castiga pesos grandes para evitar sobreajuste. C chico = más regularización = modelo más simple. |
| `max_iter` | 1000 | Máximo de iteraciones del optimizador. El valor por defecto (100) a veces no basta. En nuestro caso **convergió en 16 iteraciones**. |

### Teorema de Bayes aplicado a las alertas (clases 9 y 10)
Queremos P(fraude | alerta): si salta una alerta, ¿qué probabilidad hay de que sea fraude?

P(fraude | alerta) = P(alerta | fraude) · P(fraude) / [P(alerta | fraude) · P(fraude) + P(alerta | legítima) · P(legítima)]

- P(alerta | fraude) = recall.
- P(alerta | legítima) = tasa de falsas alarmas = FP / (FP + TN).
- P(fraude) = proporción de fraudes (prior).

**Ejemplo de la propuesta (hipotético):** recall 90 %, falsas alarmas 1 %, prior 0,172 %. El resultado es 0,9·0,00172 / (0,9·0,00172 + 0,01·0,99828) ≈ **13 %**.
Aunque el detector parece muy bueno, 87 % de sus alertas serían falsas, porque el fraude es muy raro.

**Con nuestro modelo real (validación, umbral 0,5):** recall 0,493, falsas alarmas 7 / 42.488 = 0,000165, prior 0,00167.
El resultado es 0,493·0,00167 / (0,493·0,00167 + 0,000165·0,99833) ≈ **0,833**, que es **exactamente la precisión**. La precisión *es*
P(fraude | alerta). Por eso depende tanto de la proporción de fraudes: con el mismo recall, si hay más legítimas hay más falsas alarmas.

### Lo que viene en el Avance 2 (⏳ conceptual, todavía no implementado)
- **`class_weight="balanced"`:** en el entrenamiento, cada error en un fraude pesa más (aproximadamente total / (2 · nº de fraudes)). El modelo
  deja de "ignorar" la clase minoritaria. No crea datos nuevos.
- **SMOTE:** crea fraudes **sintéticos** interpolando entre un fraude y sus vecinos más cercanos (también fraudes). Se aplica **solo al
  entrenamiento**, dentro de un `imblearn.pipeline.Pipeline`, para que nunca toque validación ni prueba (tampoco dentro de la validación cruzada).
- **Random Forest:** muchos árboles de decisión entrenados con muestras al azar de los datos y de las variables. La predicción es el
  promedio de los árboles. Captura relaciones **no lineales** e interacciones y entrega importancia de variables.
- **Isolation Forest:** no supervisado (no usa `Class` para entrenar). Construye árboles con cortes al azar. Las anomalías se aíslan con
  pocos cortes. Como puntaje de riesgo se usa `-score_samples` o `-decision_function` (más alto = más anómalo), y con eso se calcula la AUPRC.
- **Naive Bayes gaussiano (complementario):** aplica Bayes suponiendo variables independientes y con distribución normal dentro de cada clase.

---

## 4. Nuestros números

### 4.1 Duplicados

| | Filas | Fraudes | % fraude |
|---|---|---|---|
| Dataset original | 284.807 | 492 | 0,173 % |
| Duplicados eliminados | 1.081 | 19 (y 1.062 legítimas) | — |
| Dataset final | 283.726 | 473 | 0,167 % |

**Interpretación:** se pierde solo el 0,38 % de las filas y el desbalance casi no cambia. No hay copias con etiquetas contradictorias: las
mismas variables siempre tienen la misma `Class`.

### 4.2 Partición

| Conjunto | Filas | % del total | Fraudes | % fraude |
|---|---|---|---|---|
| Entrenamiento | 198.608 | 70 | 331 | 0,1667 % |
| Validación | 42.559 | 15 | 71 | 0,1668 % |
| Prueba | 42.559 | 15 | 71 | 0,1668 % |

**Interpretación:** la estratificación funcionó, porque los tres conjuntos tienen la misma proporción. Pero **validación tiene solo 71 fraudes**: cada
fraude detectado de más o de menos mueve el recall en **1,4 puntos** (1/71). Las diferencias pequeñas entre modelos pueden ser ruido.

### 4.3 Baselines en validación (umbral 0,5)

| Modelo | AUPRC | Precisión | Recall | F1 | Accuracy | TP | FP | FN | TN | Entrenamiento |
|---|---|---|---|---|---|---|---|---|---|---|
| Dummy «nunca fraude» | 0,0017 | 0 | 0 | 0 | 0,9983 | 0 | 0 | 71 | 42.488 | ~0,01 s |
| Regresión logística sin balanceo | **0,688** | 0,833 | 0,493 | 0,620 | 0,9990 | 35 | 7 | 36 | 42.481 | ~0,3 s |

**Interpretación:** el Dummy demuestra que la accuracy engaña: 99,83 % sin detectar nada. La regresión logística multiplica la AUPRC del
azar por ~400 (0,688 frente a 0,0017), pero con umbral 0,5 **se le escapa la mitad de los fraudes** (36 de 71).

### 4.4 Efecto del umbral (regresión logística, validación completa)

| Umbral | Alertas | TP | FP | FN | Precisión | Recall |
|---|---|---|---|---|---|---|
| 0,9 | 32 | 26 | 6 | 45 | 0,813 | 0,366 |
| 0,5 | 42 | 35 | 7 | 36 | 0,833 | 0,493 |
| 0,3 | 52 | 41 | 11 | 30 | 0,789 | 0,578 |
| 0,1 | 63 | 51 | 12 | 20 | 0,810 | 0,718 |
| 0,05 | 69 | 54 | 15 | 17 | 0,783 | 0,761 |
| 0,01 | 125 | 59 | 66 | 12 | 0,472 | 0,831 |

**Interpretación:**
- Al bajar el umbral de 0,5 a **0,1**, el recall sube de **0,49 a 0,72** (16 fraudes más detectados) con una caída pequeña de precisión
  (de 0,833 a 0,810: 5 falsas alarmas más).
- Bajar hasta **0,01** detecta 59 fraudes, pero las falsas alarmas se disparan (66) y la precisión cae a 0,47.
- **Por qué el umbral 0,5 no es bueno aquí:** el modelo se entrenó sin balanceo y casi todos sus puntajes son bajos. Muchos fraudes quedan con
  probabilidades bajo 0,5.
- **Cuidado:** si elegimos el umbral mirando esta tabla, ese umbral queda ajustado a validación. Su desempeño final hay que reportarlo en
  **prueba**. ⏳ La elección formal del umbral es parte del Avance 2.

### 4.5 Otras observaciones de la exploración (ejecución de prueba del notebook 01; ⏳ falta la interpretación del equipo)
- `Amount` sin duplicados: mediana **22,00** en legítimas y **9,82** en fraudes. Máximo 25.691,16 en legítimas y 2.125,87 en fraudes.
  Hay **25 fraudes con monto 0**.
- `Time` cubre **48 horas** (≈ 2 días).
- Las componentes con mayor correlación (lineal) con `Class` fueron: negativas **V17, V14, V12** y positivas **V2, V4, V11**.

---

## 5. Recorrido por el código

| Archivo | Para qué sirve | Funciones / elementos principales |
|---|---|---|
| `src/config.py` | Constantes compartidas, en un solo lugar. | `RANDOM_STATE = 42`. Rutas (`RAIZ`, `RUTA_CSV`, `DIR_MODELOS`, `DIR_CAPTURAS`). `COLUMNA_OBJETIVO = "Class"`. `PROP_TRAIN/VAL/TEST` = 0,70/0,15/0,15. |
| `src/descargar_datos.py` | Descarga el dataset desde Kaggle. | `descargar()`: usa `kagglehub.dataset_download`, copia `creditcard.csv` a `data/` y no vuelve a descargar si ya existe. Se ejecuta con `python -m src.descargar_datos`. |
| `src/datos.py` | Carga, limpieza y partición. | `cargar_datos()`: lee el CSV y quita duplicados por defecto. `eliminar_duplicados()`: muestra cuántos duplicados son fraude o legítimos y los quita. `resumen_clases()`. `particionar()`: 70/15/15 estratificada en dos pasos. `tabla_particion()`: verifica la estratificación. |
| `src/modelos.py` | Definición única de los pipelines. | `crear_logistica_sin_balanceo()`: `StandardScaler` + `LogisticRegression(lbfgs, C=1.0, max_iter=1000)`. ⏳ Aquí se agregarán los modelos del Avance 2. |
| `src/evaluacion.py` | Métricas y gráficos comunes a todos los modelos. | `evaluar(y_true, puntaje, umbral)`: AUPRC (usa el puntaje) y precisión, recall, F1, accuracy y matriz (usan la decisión). `graficar_curva_pr()`: con la línea del azar = proporción de fraudes. `graficar_matriz_confusion()`. |
| `src/entrenar_baseline.py` | Entrena y guarda el modelo para la app. | `entrenar_y_guardar()`: carga, parte, entrena con train, evalúa en validación, guarda `.joblib` (modelo + metadatos + puntajes de validación) y `.json`. `tabla_umbrales()`: métricas para 6 umbrales. |
| `src/crear_csv_ejemplo.py` | CSV pequeño para la demo. | `crear_csv_ejemplo()`: los 71 fraudes de validación + 1.929 legítimas al azar (semilla 42), mezclados → `data/ejemplo_transacciones.csv` (2.000 filas, 3,55 % de fraude). |
| `app/app.py` | Interfaz Streamlit. | `cargar_modelo()` (`st.cache_resource`), `calcular_puntajes()` (`st.cache_data`), `validar_columnas()`, `seccion_analizar()`, `seccion_resultados()`, `seccion_acerca()`. Diccionario `MODELOS` para agregar modelos. |
| `notebooks/01_exploracion.ipynb` | Exploración de datos. | Carga y tipos, nulos y duplicados (con la decisión justificada), desbalance y accuracy de «nunca fraude», `Amount` y `Time` por clase, correlación de V1–V28 con `Class`. ⏳ Falta ejecutarlo y escribir las interpretaciones (TODO). |
| `notebooks/02_baseline.ipynb` | Partición y baselines. | Partición, prueba de `evaluar()` con un ejemplo calculado a mano, AUPRC del azar, Dummy, regresión logística, tabla `docs/resultados_baseline_val.csv` y figuras en `docs/capturas/`. ⏳ Falta ejecutarlo y escribir la interpretación (sección 6, TODO). |
| `docs/diagrama_flujo.md` | Diagramas de entrenamiento y de uso en Mermaid, con la explicación de cada bloque. | ⏳ Falta exportarlos a PNG. |

**Comandos para reproducir desde cero** (detalle en `README.md`): crear el entorno → `pip install -r requirements.txt` → `python -m src.descargar_datos`
→ ejecutar los notebooks → `python -m src.entrenar_baseline` → `streamlit run app/app.py`.

---

## 6. La interfaz

### Cómo funciona Streamlit
Cada vez que el usuario toca algo (mueve el slider, sube un archivo, cambia de sección), Streamlit **vuelve a ejecutar todo el script**
`app.py`, de arriba a abajo. Por eso lo costoso se guarda en caché:
- **`@st.cache_resource` en `cargar_modelo()`:** el `.joblib` se lee **una vez** y queda en memoria, compartido entre ejecuciones. Se usa para
  objetos que no se copian, como modelos o conexiones.
- **`@st.cache_data` en `calcular_puntajes()`:** para el mismo modelo y los mismos datos, el puntaje no se recalcula. Al mover el slider solo
  se repite la comparación `puntaje ≥ umbral`, que es instantánea.

### Secciones (menú lateral)
1. **Analizar transacciones:**
   - se carga un CSV (o el de ejemplo) y se valida;
   - se calculan los puntajes y el slider fija el umbral;
   - se muestran las alertas y las aprobadas;
   - si hay `Class`: TP, FP, FN, TN, precisión, recall, AUPRC, la matriz de confusión y una tabla que compara el CSV con la **validación completa** para el mismo umbral;
   - al final, la tabla de transacciones ordenada por puntaje.
2. **Resultados del modelo:** métricas en validación, hiperparámetros, partición, tabla comparativa del baseline (si se ejecutó el notebook 02),
   **tabla de umbrales** y **curva PR** sobre la validación completa.
3. **Acerca del proyecto:** equipo, datos, licencia y declaración ética.

El aviso *"Resultados académicos; no constituyen una decisión sobre clientes reales"* aparece en todas las secciones.

### Qué valida (`validar_columnas()`)
- Que estén las 30 columnas que espera el modelo: `Time`, `V1`–`V28` y `Amount`. La lista sale de los metadatos del modelo, no está escrita a mano. Si faltan, dice cuáles.
- Que sean numéricas.
- Que no tengan valores vacíos.
- Que `Class`, si viene, tenga solo 0 o 1.
- Si no hay `Class`, la app muestra solo puntajes y alertas, porque en la vida real no se conoce la etiqueta al momento de decidir.

### El selector de modelo
Muestra solo los modelos cuyo archivo existe en `models/`. Hoy hay uno. ⏳ En el Avance 2 basta agregar una línea al diccionario `MODELOS`.

### El CSV de ejemplo: por qué de validación y por qué la precisión se ve optimista
- **Por qué de validación:** la **prueba** está reservada para la evaluación final. Usarla en cada demo, moviendo el umbral, sería tomar
  decisiones con ella. **Entrenamiento** tampoco sirve: el modelo ya vio esas filas y saldría mejor de lo real. Validación no se usó para entrenar y es donde
  está permitido explorar umbrales.
- **Por qué la precisión se ve optimista:** el ejemplo tiene los 71 fraudes de validación, pero solo 1.929 legítimas (de 42.488), unas
  **22 veces menos**. Como hay menos legítimas que puedan convertirse en falsas alarmas, los **FP se ven artificialmente bajos**.
  Con umbral 0,05:

  | Datos | TP | FP | FN | Precisión | Recall |
  |---|---|---|---|---|---|
  | CSV de ejemplo (2.000) | 54 | 1 | 17 | 0,982 | 0,761 |
  | Validación completa (42.559) | 54 | 15 | 17 | 0,783 | 0,761 |

  **El recall es igual** (son los mismos fraudes); **la precisión no**. Es el Teorema de Bayes: la precisión depende de la proporción de fraudes.
  Las cifras realistas están en *Resultados del modelo*.

---

## 7. Uso de IA generativa (IAG)

**Cómo la usamos** (detalle en `docs/registro_iag.md`, entradas 1 a 11):
- **Claude chat:** orientación inicial, plan por entregas, recomendación del dataset, borrador de la propuesta y el archivo `CLAUDE.md`.
- **Claude Code:** estructura del repo, scripts, notebooks por secciones con explicaciones, módulos de `src/`, interfaz, diagrama y esta guía.
- **Cómo trabajamos con ella:** por partes pequeñas, con explicación de cada decisión, y dejando como TODO las interpretaciones para que las escriba el equipo.

**Qué verificamos / debemos verificar:**
- Todos los números salen de **ejecutar el código**, no de la IA: conteos, métricas, tablas.
- El ejemplo pequeño de `evaluar()` (6 filas) se puede comprobar a mano y la AUPRC del azar se comprobó empíricamente.
- El notebook 02 y el script de entrenamiento dan la misma AUPRC (0,6877).
- ⏳ Los campos "Verificación hecha por el equipo", "Análisis crítico" y "Qué modificó o decidió el equipo" del registro **siguen como _(completar)_**: hay que llenarlos.

**Errores, omisiones y supuestos de la IA que detectamos o que hay que revisar:**
- **Duplicados:** la IA encontró las 1.081 filas duplicadas, pero dejó abierta la decisión. **El equipo decidió** eliminarlos *antes* de la
  partición y pidió mostrar cuántos eran fraude (19) y cómo quedaba el desbalance. Sigue siendo un **supuesto** de la IA que las copias son errores de
  registro y no transacciones reales repetidas: no hay forma de confirmarlo con el dataset.
- **Falsos positivos del CSV de ejemplo:** la IA advirtió que la precisión de la demo era optimista, pero **no lo cuantificó ni lo corrigió** en la app.
  **El equipo notó** que los FP se veían artificialmente bajos y pidió mostrar las cifras de la validación completa: 1 FP frente a 15 con umbral 0,05.
- **Pipeline definido dos veces:** el notebook 02 definía el pipeline a mano y el script lo importaba de `src/modelos.py`. El riesgo de que
  quedaran distintos fue señalado y **el equipo pidió unificarlo**.
- **Afirmaciones teóricas que conviene contrastar con fuentes** antes de la exposición:
  - que la correlación de Pearson con una clase muy desbalanceada queda acotada lejos de 1;
  - la explicación de AUPRC frente a ROC;
  - que `lbfgs` es determinista.
- **Hiperparámetros:** se usaron los valores por defecto (`C=1,0`) más `max_iter=1000`. La IA **no** buscó valores óptimos, de acuerdo con la regla del curso.
  La comparación de configuraciones la haremos nosotros en el Avance 2.

**Reflexión ética** (para completar con nuestras palabras en el Anexo IAG): la IA aceleró la parte técnica, pero las decisiones
(duplicados, uso de validación en la demo, corrección de los FP) las tomamos y verificamos nosotros. Cualquiera del equipo debe poder explicar cada parte sin la IA.

---

## 8. Limitaciones y ética

- **Variables no interpretables:** V1–V28 son componentes PCA anonimizados. Podemos predecir, pero no explicar en términos de negocio
  (comercio, país, tipo de tarjeta) por qué una transacción es sospechosa.
- **Pocos fraudes en validación y prueba:** 71 en cada uno. Cada fraude mueve el recall 1,4 puntos y las diferencias pequeñas entre modelos pueden ser ruido.
- **Duplicados:** no sabemos si son errores de registro o transacciones reales repetidas. Los eliminamos por precaución (fuga), pero es un supuesto.
- **Umbral elegido con validación:** cualquier umbral elegido mirando la tabla de validación queda ajustado a ella. El desempeño final debe
  reportarse en prueba, una sola vez. ⏳ La prueba todavía no se ha usado.
- **Partición aleatoria y no temporal:** en producción el modelo se entrena con el pasado y predice el futuro. El dataset solo cubre 2 días
  (septiembre de 2013, según la descripción en Kaggle), y los patrones de fraude cambian con el tiempo.
- **Baseline lineal y sin balanceo:** con umbral 0,5 se le escapa la mitad de los fraudes. ⏳ Mejorarlo es el objetivo del Avance 2.
- **CSV de ejemplo:** con 3,55 % de fraudes, la precisión que muestra es optimista (sección 6).
- **Costos:** no sabemos el costo real de un FN (monto perdido) frente a un FP (cliente molesto). El umbral se deja a elección del usuario.
- **Declaración ética:** *los resultados son académicos y no constituyen una decisión sobre clientes reales.* Un sistema real necesitaría
  revisión humana de las alertas, auditoría de sesgos y cumplimiento de la normativa de protección de datos.

---

## 9. Banco de 25 preguntas probables

**Responsable sugerido:** D. Canto = datos, exploración y baseline · D. Figueroa = modelos, desbalance y métricas · M. Concha = interfaz e integración.
Cualquiera puede ser interrogado sobre cualquier parte: todos deberían leer todo.

### A. Problema y datos
1. **¿Por qué no usan accuracy?** *(Canto)*
   Porque un modelo que nunca alerta logra 99,83 % de accuracy y recall 0. La accuracy está dominada por las legítimas.
   Usamos AUPRC, precisión y recall, que miden el desempeño en la clase fraude.
2. **¿Qué son V1–V28?** *(Canto)*
   Componentes principales (PCA) de las variables originales, que el banco anonimizó por confidencialidad. Sirven para predecir, pero no se pueden
   interpretar. Solo `Time` y `Amount` quedaron sin transformar.
3. **¿Por qué eliminaron los duplicados y por qué antes de partir?** *(Canto)*
   Porque si una copia queda en entrenamiento y otra en validación o prueba, el modelo se evalúa con datos que ya vio (fuga). Eran 1.081 (19 fraudes).
   Quedaron 473 fraudes y el desbalance casi no cambió (0,173 % → 0,167 %).
4. **¿Qué representa `Time`?** *(Canto)*
   Segundos desde la primera transacción del dataset, no la hora del día. Cubre unas 48 horas.
5. **¿Qué descubrieron en la exploración?** *(Canto)*
   Fuerte desbalance, sin nulos, 1.081 duplicados. La mediana de `Amount` es menor en fraudes (9,82 frente a 22,00) y algunas componentes (V17, V14,
   V12, V2, V4, V11) se relacionan más con el fraude. ⏳ La interpretación completa debe escribirla el equipo en el notebook 01.

### B. Partición y fuga de información
6. **¿Por qué la partición se hace en dos pasos?** *(Canto)*
   `train_test_split` solo divide en dos. Primero se separa 70/30 y después el 30 % en mitades (`test_size=0,5`), lo que da 15 % y 15 % del total.
7. **¿Para qué sirve estratificar?** *(Canto)*
   Para que los tres conjuntos tengan la misma proporción de fraudes (≈ 0,167 %). Con solo 473 fraudes, sin estratificar uno podría quedar con muchos menos.
8. **¿Para qué sirve validación si ya tienen prueba?** *(Figueroa)*
   Validación sirve para decidir: qué modelo, qué hiperparámetros y qué umbral. La prueba se usa una sola vez al final. Si decidiéramos con ella, su
   métrica sería optimista.
9. **¿Qué es la fuga de información y dónde la evitaron?** *(Figueroa)*
   Es que información de validación o prueba influya en el entrenamiento. La evitamos eliminando duplicados antes de partir, escalando dentro del
   pipeline y sin tocar la prueba. En el Avance 2, SMOTE irá solo en entrenamiento.

### C. Modelo y métricas
10. **¿Cómo funciona la regresión logística?** *(Figueroa)*
    Combina linealmente las variables y pasa el resultado por la sigmoide, que lo convierte en una probabilidad de fraude (nuestro puntaje). Los pesos se
    aprenden minimizando la log-loss. Es un clasificador lineal.
11. **¿Qué hacen C, solver y max_iter?** *(Figueroa)*
    C es el inverso de la regularización L2 (más chico = modelo más simple). `lbfgs` es el algoritmo de optimización. `max_iter` es el máximo de
    iteraciones: pusimos 1000 por seguridad y convergió en 16.
12. **¿Por qué el `StandardScaler` está dentro del pipeline?** *(Figueroa)*
    Para que su media y desviación se calculen solo con entrenamiento y se reutilicen en validación y prueba. Escalar antes de partir filtraría información.
    Hace falta porque `Amount` y `Time` tienen escalas muy distintas a V1–V28.
13. **¿Qué es la AUPRC y por qué es la métrica principal?** *(Figueroa)*
    Es el área bajo la curva Precisión-Recall, que resume el desempeño para todos los umbrales. No depende del umbral y se concentra en la clase
    fraude. Nuestro baseline obtiene 0,688.
14. **¿Por qué la AUPRC del azar es igual a la proporción de fraudes?** *(Figueroa)*
    Con puntajes aleatorios, cualquier grupo de alertas tiene la misma proporción de fraudes que el total, así que la precisión es ≈ 0,00167 en todo
    recall. Lo comprobamos: dio 0,00163.
15. **¿Por qué no AUC-ROC?** *(Figueroa)*
    La ROC usa FP / (FP + TN). Con 42.488 legítimas, muchas falsas alarmas producen una tasa pequeña y la curva se ve optimista. La precisión sí
    refleja esas falsas alarmas.
16. **¿Qué significa precisión 0,833 y recall 0,493?** *(Figueroa)*
    De cada 6 alertas, 5 son fraude (35 de 42). Pero solo se detecta la mitad de los fraudes (35 de 71): se escapan 36.
17. **¿Por qué el Dummy tiene AUPRC 0,0017?** *(Canto)*
    Da el mismo puntaje (0) a todas las transacciones, así que no ordena nada. Su curva PR queda igual a la del azar, a la altura de la proporción de fraudes.
18. **¿Es 0,5 un buen umbral?** *(Figueroa)*
    No necesariamente. Con 0,1 el recall sube de 0,49 a 0,72 y la precisión baja poco (0,833 → 0,810). Pero el umbral debe elegirse en validación y
    reportarse en prueba. ⏳ Es parte del Avance 2.
19. **¿Cómo se conecta con el Teorema de Bayes?** *(Figueroa)*
    La precisión es P(fraude | alerta). Por Bayes depende del recall, de la tasa de falsas alarmas y del prior (0,167 %). Con nuestros números da 0,833,
    igual a la precisión medida. Con un prior tan bajo, incluso pocas falsas alarmas bajan mucho la precisión.

### D. Interfaz e integración
20. **¿Cómo llega el modelo a la interfaz?** *(Concha)*
    `python -m src.entrenar_baseline` entrena y guarda un `.joblib` con el pipeline, los metadatos y los puntajes de validación. La app lo carga con
    `joblib` una sola vez (`st.cache_resource`) y no reentrena.
21. **¿Qué pasa cuando muevo el slider?** *(Concha)*
    Streamlit vuelve a ejecutar el script. El modelo y los puntajes vienen de la caché, así que solo se recalcula `puntaje ≥ umbral` y las métricas. Por eso
    es instantáneo.
22. **¿Qué pasa si subo un CSV sin la columna `Amount`?** *(Concha)*
    `validar_columnas()` lo detecta y muestra un error con las columnas que faltan, sin llegar al modelo. También revisa que sean numéricas, sin vacíos, y que
    `Class`, si viene, sea 0 o 1.
23. **¿Por qué el CSV de ejemplo sale de validación y no de prueba?** *(Concha)*
    La prueba está reservada para la evaluación final. Usarla en las demos sería mirarla y decidir con ella. Entrenamiento tampoco sirve, porque el modelo ya vio esas filas.
24. **¿Por qué en la demo la precisión es tan alta?** *(Concha)*
    El ejemplo tiene ~22 veces menos legítimas que la validación, así que hay menos falsas alarmas posibles. Con umbral 0,05 hay 1 FP en el ejemplo y 15 en la
    validación completa, con el mismo recall. La app muestra ambas cifras lado a lado.

### E. IAG y ética
25. **¿Qué hizo la IA y cómo lo verificaron?** *(todos)*
    Apoyó con el código, la estructura y las explicaciones, por partes. Los números salen de ejecutar el código, y comprobamos `evaluar()` a mano y la AUPRC
    del azar empíricamente. Detectamos que la demo subestimaba los FP y decidimos nosotros cómo tratar los duplicados; todo queda en `docs/registro_iag.md`.

---

## 10. Glosario

| Término | Significado breve |
|---|---|
| **Accuracy** | Proporción de predicciones correctas. Engaña con clases desbalanceadas. |
| **AUPRC / Average Precision** | Área bajo la curva Precisión-Recall. Métrica principal; el azar ≈ proporción de fraudes. |
| **AUC-ROC** | Área bajo la curva ROC (tasa de verdaderos positivos frente a tasa de falsos positivos). El azar = 0,5. Optimista con mucho desbalance. |
| **Baseline** | Modelo de referencia simple que los modelos propuestos deben superar. |
| **`class_weight`** | Parámetro que da más peso a los errores en la clase minoritaria durante el entrenamiento. ⏳ Avance 2. |
| **Desbalance de clases** | Una clase mucho más frecuente que la otra (aquí 0,167 % de fraudes). |
| **Dummy** | Clasificador trivial (aquí: siempre "legítima") usado como piso. |
| **Estratificación** | Partir manteniendo la proporción de clases en cada conjunto. |
| **F1** | Media armónica de precisión y recall. |
| **Falso negativo (FN)** | Fraude que el modelo aprueba: dinero perdido. |
| **Falso positivo (FP)** | Transacción legítima que el modelo alerta: cliente molesto. |
| **Fuga de información** | Información de validación o prueba que influye en el entrenamiento y vuelve optimistas las métricas. |
| **Hiperparámetro** | Configuración del modelo que se fija antes de entrenar (C, `max_iter`…), a diferencia de los pesos, que se aprenden. |
| **Isolation Forest** | Modelo no supervisado que detecta anomalías aislándolas con cortes al azar. ⏳ Avance 2. |
| **joblib** | Librería para guardar y cargar objetos de Python (el modelo entrenado) en un archivo. |
| **lbfgs** | Algoritmo de optimización cuasi-Newton que usa la regresión logística para encontrar los pesos. |
| **Matriz de confusión** | Tabla 2×2 de TP, FP, FN y TN. |
| **PCA** | Análisis de componentes principales: transforma variables en combinaciones lineales no correlacionadas. |
| **Pipeline** | Cadena de pasos (escalado → modelo) que se ajusta y aplica como una sola unidad. Evita fugas. |
| **Precisión** | TP / (TP + FP): de las alertas, cuántas eran fraude. Es P(fraude \| alerta). |
| **Puntaje de riesgo** | Probabilidad estimada de fraude que entrega el modelo (0 a 1). |
| **Random Forest** | Conjunto de árboles de decisión entrenados con muestras al azar; promedia sus predicciones. ⏳ Avance 2. |
| **Recall** | TP / (TP + FN): de los fraudes reales, cuántos se detectan. |
| **Regresión logística** | Clasificador lineal que convierte una combinación lineal en probabilidad mediante la sigmoide. |
| **Regularización (L2)** | Penalización a los pesos grandes para evitar sobreajuste; su fuerza es 1/C. |
| **Semilla (`random_state`)** | Número que fija el azar para que los resultados sean reproducibles (aquí 42). |
| **Sigmoide** | Función 1 / (1 + e⁻ᶻ) que transforma cualquier número en un valor entre 0 y 1. |
| **SMOTE** | Técnica que crea ejemplos sintéticos de la clase minoritaria interpolando entre vecinos; solo en entrenamiento. ⏳ Avance 2. |
| **StandardScaler** | Transforma cada variable a media 0 y desviación estándar 1. |
| **Streamlit** | Librería de Python para crear interfaces web; re-ejecuta el script en cada interacción. |
| **Umbral de decisión** | Valor desde el cual un puntaje se convierte en alerta. |
| **Validación / prueba** | Validación: para decidir. Prueba: para reportar una sola vez al final. |
