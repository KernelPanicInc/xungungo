import streamlit as st
import feedparser
from st_click_detector import click_detector
from datetime import datetime

nombre = "Bloomberg News"
descripcion = "Este plugin muestra las últimas noticias de Bloomberg en formato de tabla clickeable."
tipo = "news"

def render():
    st.title("Noticias de Bloomberg")
    
    # Función para obtener las noticias desde el feed RSS de Bloomberg
    @st.cache_data(show_spinner=False)
    def get_news():
        feed_url = "https://feeds.bloomberg.com/news.rss"
        feed = feedparser.parse(feed_url)
        return feed.entries

    news_items = get_news()
    
    # Ordenar noticias por fecha (si hay información disponible)
    def parse_date(entry):
        try:
            return datetime.strptime(entry.get("published", ""), "%a, %d %b %Y %H:%M:%S %Z")
        except ValueError:
            return datetime.min
    
    news_items.sort(key=parse_date, reverse=True)
    
    # Crear tabla HTML con estilo oscuro y enlaces clickeables
    table_html = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: #1e1e1e;
            color: white;
        }
        th, td {
            border: 1px solid #444;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #333;
        }
        tr:hover {
            background-color: #555;
        }
        a {
            color: #1e90ff;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
    <table>
        <tr>
            <th>Título</th>
            <th>Autor</th>
            <th>Fecha</th>
        </tr>
    """
    
    for entry in news_items:
        title = entry.get("title", "Sin título")
        author = entry.get("author", "Desconocido")
        date = entry.get("published", "")
        link = entry.get("link", "#")
        table_html += f"<tr><td><a href='#' id='{link}'>{title}</a></td><td>{author}</td><td>{date}</td></tr>"
    
    table_html += "</table>"
    
    # Mostrar tabla y detectar clics
    clicked = click_detector(table_html)
    
    if clicked:
        st.markdown(f"[Abrir noticia]({clicked})")