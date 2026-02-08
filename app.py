import streamlit as st
import asyncio, os, datetime, hashlib, re
from playwright.async_api import async_playwright
from supabase import create_client

# 1. CLOUD BROWSER INSTALLER
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    os.system("playwright install chromium --with-deps")

st.set_page_config(page_title="Tennis Sniper Pro", page_icon="🎾")

# 2. SUPABASE CONNECTION
try:
    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error(f"Config Error: {e}"); st.stop()

st.title("🎾 Tennis Sniper Pro")

# 3. DATE LOGIC (Auto/Manual Toggle)
with st.sidebar:
    st.subheader("📅 Target Settings")
    use_auto = st.toggle("Use 8-Day Auto-Strike", value=True)
    if use_auto:
        target_date = datetime.date.today() + datetime.timedelta(days=8)
    else:
        target_date = st.date_input("Select Date", datetime.date.today() + datetime.timedelta(days=8))
    
    st.subheader("🔑 Credentials")
    u_email = st.text_input("Club Email")
    u_pass = st.text_input("Club Password", type="password")
    
    st.subheader("⏰ Time Window")
    s_time = st.time_input("Start", datetime.time(9, 0))
    e_time = st.time_input("End", datetime.time(16, 0))

st.metric("Target Date", target_date.strftime("%A, %b %d"))

# 4. SNIPER ENGINE
async def run_snipe(t_date, t_start, t_end):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = await browser.new_page()
        try:
            st.info(f"Attempting login for {t_date}...")
            await page.goto("https://www.lifetime.life/login", timeout=60000)
            await page.fill('input[name="username"]',
