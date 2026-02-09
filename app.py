import streamlit as st
import time
import subprocess
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Tennis Sniper Pro", page_icon="🎾", layout="wide")

# --- BOOTSTRAP PLAYWRIGHT FOR CLOUD ---
def install_playwright():
    if not os.path.exists("/home/appuser/.cache/ms-playwright"):
        with st.spinner("Installing Cloud Browsers... this may take a minute."):
            subprocess.run(["python", "-m", "playwright", "install", "chromium"])

install_playwright()

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
            days_to_wait = (window_open_date - now.date()).days
            
            msg = f"Waiting {days_to_wait} day(s) until window opens" if days_to_wait > 0 else "Standing by for 9:00 AM Strike"

            status_text.markdown(f"""
                <div style='text-align:center; padding:30px; border:2px solid #238636; border-radius:15px;'>
                    <p style='color:#8b949e; text-transform:uppercase; letter-spacing:2px;'>{msg}</p>
                    <h1 style='font-family:monospace; font-size:80px; color:#ffffff;'>{curr_t}</h1>
                </div>
            """, unsafe_allow_html=True)
            
            if now.date() >= window_open_date and now.hour >= 9:
                break
            time.sleep
