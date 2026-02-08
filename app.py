import streamlit as st
import asyncio
import os
import datetime
import hashlib, re
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

# 3. DATE LOGIC (Manual Override Restored)
st.sidebar.subheader("📅 Target Settings")
use_auto = st.sidebar.toggle("Use 8-Day Auto-Strike", value=True)

if use_auto:
    target_date = datetime.date.today() + datetime.timedelta(days=8)
    st.metric("Auto-Target Date", target_date.strftime("%A, %b %d"))
else:
    target_date = st.sidebar.date_input("Select Date", datetime.date.today() + datetime.timedelta(days=8))
    st.metric("Manual Target Date", target_date.strftime("%A, %b %d"))

# 4. PREFERENCES & CONTROLS
with st.sidebar:
    st.subheader("🔑 Credentials")
    user_email = st.text_input("Club Email")
    user_pass = st.text_input("Club Password", type="password")
    st.subheader("⏰ Time Window")
    start_time = st.time_input("Earliest Start", datetime.time(9, 0))
    end_time = st.time_input("Latest End", datetime.time(16, 0))
    if st.button("Save Preferences"):
        sb.table("sniper_prefs").upsert({"id": 1, "email": user_email, "min_time": str(start_time), "max_time": str(end_time)}).execute()
        st.success("Preferences Saved")

# 5. SNIPER EXECUTION ENGINE
async def run_snipe_sequence(target_d, start_t, end_t):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context()
        page = await context.new_page()
        try:
            st.info(f"Logging in to reserve for {target_d}...")
            await page.goto("https://www.lifetime
