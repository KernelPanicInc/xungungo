import streamlit as st
import utils.set_logo as set_logo

st.set_page_config(
    page_title="Xungungo Stocks",
    page_icon="👋",
    layout="wide",
)

set_logo.set_logo()

st.write("# Welcome to Xungungo! 👋")

