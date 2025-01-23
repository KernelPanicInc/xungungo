import streamlit as st
import plugins.dashboard.dashboard as dashboard
import plugins.dashboard.config_page as config_page



def get_dashboard():        
    dashboard.render()
