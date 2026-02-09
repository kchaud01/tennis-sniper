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
            time.sleep(1)
        
        if not st.session_state.armed:
            st.warning("Mission Aborted.")
            return

    final_url = target_url.replace("REPLACE_DATE", target_date_str).replace("REPLACE_DUR", str(duration))
    
    with st.status(f"🚀 STRIKING {club_name}...", expanded=True):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
                page = browser.new_page()
                
                def login():
                    if page.locator('input[type="password"]').is_visible(timeout=10000):
                        page.locator('input[name="username"], #loginId').first.fill(email)
                        page.locator('input[type="password"]').first.fill(password)
                        page.locator('button:visible').filter(has_text="Log In").first.click()
                        page.wait_for_load_state("networkidle")

                page.goto(final_url, wait_until="networkidle")
                login()
                page.wait_for_selector(".timeslot", timeout=30000)
                page.evaluate("document.querySelectorAll('.modal-backdrop, .ot-sdk-container, #chat-container').forEach(el => el.remove());")
                
                slots = page.locator(".timeslot").all()
                target_node = None
                for slot in slots:
                    txt = slot.locator(".timeslot-time").inner_text().upper().strip()
                    try:
                        slot_min = get_minutes(txt)
                        if slot_min >= earliest_minutes and "RESERVED" not in slot.inner_text().upper():
                            target_node = slot
                            break
                    except: continue

                if target_node:
                    target_node.click(force=True)
                    time.sleep(5)
                    login()
                    for _ in range(15):
                        page.evaluate("() => { const b = Array.from(document.querySelectorAll('button')).find(x => x.innerText.includes('Finish')); if(b) b.click(); }")
                        if "success" in page.url.lower() or page.locator("text=Confirmed").is_visible(timeout=1500):
                            st.balloons()
                            st.success(f"🏆 SECURED: {target_date_str}!")
                            break
                        time.sleep(1.0)
                else: st.error("❌ NO SLOTS FOUND")
                browser.close()
        except Exception as e:
            st.error(f"🚨 CLOUD ERROR: {e}")
    
    st.session_state.armed = False

# --- MAIN UI ---
st.title("🎾 Tennis Sniper Pro")
times = [f"{h if h<=12 else h-12}:{m} {'AM' if h<12 else 'PM'}" for h in range(4, 22) for m in ["00", "30"]]

with st.sidebar:
    st.header("⚙️ MISSION CONFIG")
    club_choice = st.selectbox("Club", ["Peachtree Corners (Indoor)", "North Druid Hills (Outdoor)"])
    u_email = st.text_input("Email", value="koushikchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    u_date = st.date_input("Target Play Date", value=datetime.now() + timedelta(days=8))
    u_start_t = st.selectbox("Start Time", options=times, index=2)
    u_dur = st.selectbox("Duration (Min)", options=[60, 90], index=1)
    wait_window = st.checkbox("Wait for 9:00 AM Window", value=True)

# URL logic built to avoid long lines that cause clipping
pc_base = "
