import streamlit as st
import os
import subprocess
import time
from datetime import datetime, timedelta

# --- AUTOMATIC BROWSER INSTALLER ---
# This must run BEFORE importing sync_playwright to avoid path errors
def force_playwright_install():
    if not os.path.exists("/home/appuser/.cache/ms-playwright"):
        with st.spinner("Installing Chromium for Streamlit Cloud..."):
            try:
                subprocess.run(["python", "-m", "playwright", "install", "chromium"], check=True)
            except Exception as e:
                st.error(f"Installation failed: {e}")

force_playwright_install()

# Now we can safely import Playwright
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Tennis Sniper Pro", page_icon="🎾", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    [data-testid="stMetric"] { 
        background-color: #161b22 !important; 
        border: 1px solid #30363d !important;
        padding: 20px; border-radius: 10px;
    }
    div.stButton > button { border-radius: 8px; font-weight: bold; height: 3.5em; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

if 'armed' not in st.session_state:
    st.session_state.armed = False

def run_sniper(email, password, target_date_obj, earliest_time_str, wait_for_window, target_url, club_name, duration):
    def get_minutes(t_str):
        t = datetime.strptime(t_str, "%I:%M %p")
        return t.hour * 60 + t.minute

    earliest_minutes = get_minutes(earliest_time_str)
    target_date_str = target_date_obj.strftime('%Y-%m-%d')
    window_open_date = target_date_obj - timedelta(days=8)

    if wait_for_window:
        status_text = st.empty()
        while st.session_state.armed:
            now = datetime.now()
            curr_t = now.strftime("%H:%M:%S")
            days_to_wait = (window_open_date - now.date()).
