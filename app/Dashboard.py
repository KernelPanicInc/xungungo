import streamlit as st
import utils.set_logo as set_logo
import plugins.dashboard.dashboard as dashboard
st.set_page_config(
    page_title="Xungungo Stocks",
    page_icon="👋",
    layout="wide",
)

set_logo.set_logo()

dashboard.render()
#st.switch_page("pages/1_Stocks.py")

