import streamlit as st
import wikiquote
import html

nombre = "Frase del Día"
descripcion = "Plugin que muestra la frase del día con HTML estilizado, removiendo caracteres especiales y adaptándose al modo oscuro, con altura configurable."
tipo = "quote"

default_config = {
    "lang": "es",
    "height": 300  # Altura por defecto en píxeles
}

def config(current_config: dict) -> dict:
    st.write("### Configuración de la Frase del Día")
    lang = st.selectbox(
        "Selecciona el idioma",
        options=["en", "es", "fr", "de", "it", "pl", "pt"],
        index=["en", "es", "fr", "de", "it", "pl", "pt"].index(
            current_config.get("lang", default_config["lang"])
        ),
        help="Selecciona el idioma en el que se mostrará la frase del día."
    )
    height = st.slider(
        "Altura del widget (px)",
        min_value=100,
        max_value=600,
        value=current_config.get("height", default_config["height"]),
        step=50,
        help="Define la altura en píxeles del contenedor de la frase."
    )
    return {"lang": lang, "height": height}

def render(config: dict):
    lang = config.get("lang", default_config["lang"])
    height = int(config.get("height", default_config["height"]))-70  # Restar 30px para el margen superior e inferior
    # Se espera que config["is_dark"] venga desde el dashboard (por defecto, False)
    is_dark = config.get("is_dark", False)
    
    try:
        # Obtiene la frase del día (retorna (quote, author))
        quote, author = wikiquote.quote_of_the_day(lang=lang)
    except Exception as e:
        st.error(f"Error al obtener la frase del día: {e}")
        return

    # Remover espacios y comillas extrañas al inicio y final
    quote = quote.strip('«»"').strip()
    author = author.strip('«»"').strip()

    # Escapar caracteres especiales para HTML
    quote_escaped = html.escape(quote)
    author_escaped = html.escape(author)

    # Configurar colores según el tema
    if is_dark:
        bg_gradient = "linear-gradient(135deg, #2c2c2c 0%, #1a1a1a 100%)"
        text_color_quote = "#ffffff"
        text_color_author = "#cccccc"
        border = "1px solid #444"
        box_shadow = "0 4px 8px rgba(0,0,0,0.5)"
    else:
        bg_gradient = "linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%)"
        text_color_quote = "#333333"
        text_color_author = "#555555"
        border = "1px solid #ddd"
        box_shadow = "0 4px 8px rgba(0,0,0,0.1)"

    # Generar HTML estilizado para un "card" moderno usando la altura configurada
    html_content = f"""
    <div style="
         max-width: 800px;
         margin: 20px auto;
         padding: 20px;
         border: {border};
         border-radius: 10px;
         box-shadow: {box_shadow};
         background: {bg_gradient};
         font-family: 'Helvetica', sans-serif;
         height: {height}px;
         overflow: auto;
         ">
         <p style="
             font-size: 1.5em;
             color: {text_color_quote};
             text-align: center;
             margin: 0 0 10px 0;
         ">&ldquo;{quote_escaped}&rdquo;</p>
         <p style="
             font-size: 1.2em;
             color: {text_color_author};
             text-align: right;
             margin: 0;
             font-style: italic;
         ">— {author_escaped}</p>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
