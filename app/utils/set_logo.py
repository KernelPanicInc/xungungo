import streamlit as st
import base64

def set_logo(logo_path = "static/xungungo.png"):
    with open(logo_path, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    logo_path = f"data:image/png;base64,{logo_base64}"
    logo_html = f"""
    <style>
    [data-testid="stSidebarNav"] {{
        background-image: url({logo_path});
        background-repeat: no-repeat;
        padding-top: 115px;
        background-position: center top;
        background-size: 40%;
    }}
    </style>
    """
    st.markdown(logo_html, unsafe_allow_html=True)
    # Transparent 1x1 pixel base64 image
    transparent_pixel = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    st.logo(
        image=transparent_pixel,
        icon_image=logo_path
    )