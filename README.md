# 📈 Xungungo

**Xungungo** es una aplicación de escritorio basada en [Streamlit](https://streamlit.io/) que facilita el análisis de acciones, la visualización de indicadores técnicos y la consulta de noticias financieras, todo desde una interfaz amigable.

---

## 🧭 ¿Qué puedes hacer con Xungungo?

- 🔍 **Buscar** cualquier acción por su símbolo (AAPL, MSFT, TSLA…).
- 📊 **Graficar** velas e historial de precios con un clic.
- 📈 **Añadir indicadores** populares (SMA, RSI, MACD y más).
- 📰 **Leer noticias** recientes sobre el mercado.
- 🧩 **Activar plugins** que amplían la funcionalidad (screeners, dark‑pools, forecasting, etc.).

---

## 🚀 Instalación rápida (Windows)

1. Ve a la pestaña **Releases** del repositorio.
2. Descarga el instalador más reciente (`Xungungo.zip`).
3. Ejecuta el asistente y sigue los pasos (no necesitas tener Python instalado).
4. Al terminar, encontrarás un acceso directo en tu menú Inicio.

> **¡Listo!** Inicia Xungungo y empieza a explorar los mercados.

---

## ⚙️ Instalación manual (avanzada / otras plataformas)

### Requisitos

- **Python ≥ 3.9**
- Git (opcional, para clonar el repositorio)

### Pasos

```bash
# 1. Clona o descarga el proyecto
$ git clone https://github.com/tuusuario/xungungo.git
$ cd xungungo

# 2. Crea (opcional) y activa un entorno virtual
$ python -m venv venv
$ source venv/bin/activate   # Linux/macOS
# .\venv\Scripts\activate  # Windows PowerShell

# 3. Instala dependencias
$ pip install -r requirements.txt

# 4. Ejecuta la app
$ streamlit run app/Dashboard.py
```

La aplicación se abrirá automáticamente en tu navegador predeterminado.

---

## 🧩 Plugins incluidos

| Plugin                     | Descripción                                      |
| -------------------------- | ------------------------------------------------ |
| **Charts**                 | Gráfico principal de velas + volumen             |
| **SMA (3 Medias Móviles)** | Añade hasta tres medias móviles configurables    |
| **Screeners**              | Lista acciones que cumplen criterios específicos |
| **Dark Pools**             | Muestra actividad inusual en mercados oscuros    |
| **News (Bloomberg, etc.)** | Noticias financieras recientes                   |

*(Esta lista crece de forma constante; revisa la barra lateral para ver todos los disponibles.)*

---

## 📸 Capturas de pantalla

> Próximamente: aquí añadiremos imágenes de la interfaz, ejemplos de gráficos y la vista de plugins para que te hagas una idea rápida de cómo luce Xungungo.

---

## 🖥️ Requisitos principales (modo manual)

Los módulos clave que utiliza Xungungo son:

- `streamlit` – interfaz web/desktop
- `yfinance` – obtención de datos históricos y en tiempo real
- `streamlit-lightweight-charts` – gráficas interactivas estilo TradingView
- `pandas` & `numpy` – manipulación de datos

Consulta [`requirements.txt`](./requirements.txt) para la lista completa.

---

## 🙌 Contribuye

¿Te gustaría proponer un plugin, reportar un error o mejorar la documentación? ¡Eres bienvenido!

1. Abre un *Issue* con el detalle.
2. Para código, crea un *fork*, haz tus cambios en una rama y envía un *Pull Request*.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

