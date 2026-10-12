# Extractor Facebook HAR + IA

Aplicación Streamlit para importar capturas HAR de Facebook, extraer publicaciones, clasificarlas con Gemini, corregir manualmente los resultados y generar reportes Excel. Incluye estadísticas, respaldo JSON y recuperación de correcciones.

## Desplegar en Streamlit Community Cloud

1. Sube el contenido de este repositorio a GitHub.
2. En [Streamlit Community Cloud](https://share.streamlit.io/), crea una aplicación y selecciona el repositorio y la rama.
3. Establece `app.py` como **Main file path**.
4. Despliega. Streamlit instalará las dependencias de `requirements.txt`.

No necesitas Node.js para ejecutar la aplicación. Los archivos JavaScript se integran en la interfaz por `web_bundle.py` y se ejecutan en el navegador.

## Ejecutar localmente

Requiere Python 3.9 o posterior.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Flujo de trabajo

1. En Facebook, abre las herramientas de desarrollador del navegador, entra a **Network/Red**, conserva el registro mientras recorres las publicaciones y exporta un HAR **con contenido**. Un HAR sin cuerpos de respuesta puede no incluir publicaciones recuperables.
2. En la aplicación, carga uno o varios archivos `.har` y pulsa **Analizar HAR**.
3. Selecciona la cuenta y el periodo, revisa el resultado y pulsa **Aplicar cuenta y periodo**.
4. Si deseas clasificación asistida, introduce una clave de Gemini y pulsa **Clasificar con IA**. Sin clave se pueden exportar los resultados obtenidos con reglas locales, marcando los casos que necesitan revisión.
5. Revisa o corrige formato, pertenencia y tema. Descarga el Excel y, si lo necesitas, un respaldo JSON o CSV.

## Qué contiene el Excel

- **Publicaciones:** fecha/hora, bloque operativo, texto, formato, pertenencia, tema, red, autor, enlace, revisión y motivos.
- **Estadísticas:** conteos y porcentajes por formato, pertenencia, red, mes y tema.

El libro se genera con el escritor XLSX incluido (`xlsx.js`); no depende de una biblioteca remota para crear Excel. Las celdas son editables. Las fórmulas de estadísticas actualizan los conteos de las filas existentes; si se agregan filas manualmente, hay que ampliar los rangos.

## Funciones conservadas

- Extracción de HAR de Facebook y eliminación de duplicados.
- Clasificación con Gemini y reglas locales.
- Correcciones manuales de formato, pertenencia y tema.
- Estadísticas de publicaciones.
- Guardado local en el navegador e importación/exportación de respaldos JSON.
- Importación de correcciones desde CSV.
- Exportación a XLSX y CSV.
- Compatibilidad de respaldos con el esquema de la extensión institucional.

## Privacidad y límites

El HAR se procesa en el navegador; no se carga a Python ni se conserva el HAR completo en el servidor. Al usar Gemini, el texto y las imágenes accesibles se envían a Google para su clasificación. La clave se mantiene en el campo de la sesión y no se guarda en `localStorage` ni se incluye en respaldos. No publiques HAR, respaldos, claves ni archivos `secrets.toml` en GitHub.

La cantidad de publicaciones recuperables depende de lo que Facebook haya incluido en la captura. La herramienta no navega Facebook por su cuenta ni garantiza que el HAR represente todas las publicaciones del periodo. El límite de publicaciones por reporte es 5,000.

## Estructura

- `app.py`: punto de entrada de Streamlit.
- `web_bundle.py`: incorpora los archivos web para que no dependan de rutas relativas.
- `index.html` y `styles.css`: interfaz.
- `app.js`, `core.js`, `facebook-data.js`, `har-*.js`, `report*.js`: flujo de extracción y reporte.
- `ai*.js` y `gemini.js`: clasificación con IA.
- `archive-*.js`: persistencia y transferencia de respaldos/correcciones.
- `statistics.js`, `xlsx.js`, `excel.js`: estadísticas y exportación.
- `.streamlit/config.toml`: configuración de Streamlit.
- `tests/`: pruebas automatizadas.

## Ejecutar las pruebas

Requiere Python y Node.js 18 o posterior. No se necesita una clave de Gemini ni se hacen llamadas reales a la API durante las pruebas.

```bash
python -m unittest discover -s tests -v
node tests/report.cjs
node tests/gemini.cjs
node tests/interface.cjs
```

Las pruebas de interfaz y Gemini simulan el navegador y las respuestas de la API. No sustituyen una prueba manual con una captura HAR real y una clave válida.
