# Progreso del proyecto — Detección de fraude (Tema 12, IA 2026-2, UBB)

> Archivo para dar contexto a Claude chat. Lo mantiene Claude Code al día después de cada sesión.
> El contexto completo del proyecto (reglas, objetivos, decisiones técnicas, fechas) está en `CLAUDE.md`.

**Foco actual:** Avance 1. Plazo en Moodle: **mié 18 nov 2026, 23:59**. Exposición: jue 19 nov.

---

## Estado actual (2026-11-07)

### Hecho
- Raíz del proyecto: `C:\Users\coee1\Desktop\ProyectoIA` (se usa directamente como raíz del repo; no hay subcarpeta `fraude-tema12/`).
- `git init` hecho (aún sin commits ni remoto en GitHub).
- Carpetas creadas: `data/`, `notebooks/`, `src/`, `models/`, `app/`, `docs/capturas/`, `informe/` (las vacías llevan `.gitkeep`).
- `.gitignore`: excluye `data/*.csv`, `models/*.joblib`, `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`.
- `src/config.py`: `RANDOM_STATE = 42`, rutas (`RAIZ`, `DIR_DATOS`, `DIR_MODELOS`, `DIR_CAPTURAS`, `RUTA_CSV`), `DATASET_KAGGLE = "mlg-ulb/creditcardfraud"`, `COLUMNA_OBJETIVO = "Class"`, proporciones 0.70 / 0.15 / 0.15.
- `src/descargar_datos.py`: descarga con `kagglehub.dataset_download(...)` y copia `creditcard.csv` a `data/`. No vuelve a descargar si ya existe. Se ejecuta con `python -m src.descargar_datos` desde la raíz.
- `requirements.txt`: pandas, numpy, scikit-learn, imbalanced-learn, matplotlib, seaborn, streamlit, joblib, kagglehub, jupyter (**sin versiones fijadas todavía**).
- `docs/registro_iag.md` creado con las entradas previas.

### Decisiones tomadas
- **Duplicados eliminados antes de la partición** (evita fuga train→test). De las 1.081 copias, 1.062 son legítimas y 19 fraudes; no hay copias con etiqueta contradictoria. Dataset final: **283.726 filas, 473 fraudes (0,167 %)**. Implementado en `src/datos.py` (`cargar_datos()` lo aplica por defecto; `eliminar_duplicados()`, `resumen_clases()`).
- Git lo maneja Maximiliano: Claude Code no hace commits.

### Pendiente inmediato
- [x] Entorno `.venv` (Python 3.14.7) creado y dependencias instaladas sin errores.
- [x] Versiones fijadas en `requirements.txt` (scikit-learn 1.9.1, imbalanced-learn 0.14.2, pandas 3.1.1, numpy 2.5.4, streamlit 1.67.0, etc.).
- [x] Dataset descargado (`python -m src.descargar_datos`) y verificado: 284.807 filas × 31 columnas, 492 fraudes (0,173 %), 0 nulos, **1.081 filas duplicadas** (decidir en la exploración si se eliminan).
- [x] `README.md` con instalación desde cero, fuente/licencia/cita de datos y estructura.

### Checklist Avance 1
- [ ] Diagrama de flujo (CSV → preprocesamiento → modelo → puntaje → umbral → aprobar/alertar + métricas)
- [~] `notebooks/01_exploracion.ipynb`: creado (8 secciones: qué/por qué → código → preguntas de exposición). Verificado que corre sin errores. **Falta:** que Daniel lo ejecute (genera las figuras en `docs/capturas/`) y escriba las interpretaciones/conclusiones marcadas TODO.
- [ ] `notebooks/02_baseline.ipynb`: partición 70/15/15 estratificada, Dummy + regresión logística sin balanceo (AUPRC, precisión, recall, matriz de confusión, accuracy)
- [ ] Capturas/logs de las primeras pruebas
- [ ] Documentación del entrenamiento (hiperparámetros, partición, resultados preliminares)
- [ ] Borrador de `app/app.py` (Streamlit)
- [ ] Registro IAG al día

---

## Próximo paso sugerido
1. Daniel ejecuta y completa los TODO de `01_exploracion.ipynb`.
2. `notebooks/02_baseline.ipynb`: agregar la partición estratificada 70/15/15 a `src/datos.py`, Dummy + regresión logística sin balanceo.

---

## Historial de sesiones con Claude Code
- **2026-11-07:** lectura de `CLAUDE.md`; estructura del repo, `.gitignore`, `config.py`, `descargar_datos.py`, `requirements.txt`, `registro_iag.md` y este archivo.
- **2026-11-07 (cont.):** entorno instalado y versiones fijadas; dataset descargado y verificado; `README.md`.
- **2026-11-07 (cont. 2):** `src/datos.py` (carga + eliminación de duplicados) y `notebooks/01_exploracion.ipynb`.
