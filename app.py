import streamlit as st
import asyncio
import os
import datetime
import hashlib, re
from playwright.async_api import async_playwright
from supabase import create_client

# 1. CLOUD ENVIRONMENT FIX
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    os.system("playwright install chromium --with-deps")

st.set_page_config(page_title="Tennis Sniper Pro", page_icon="🎾")

# 2. SUPABASE CONNECTION
try:
    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except Exception as e:
    st.error(f"Config Error: {e}"); st.stop()

st.title("🎾 Tennis Sniper Pro")

# 3. DATE LOGIC (8-Day Lead Time)
today = datetime.date.today()
target_date = today + datetime.timedelta(days=8)
st.metric("Target Booking Date", target_date.strftime("%A, %b %d"))

# 4. PREFERENCES & CONTROLS
with st.sidebar:
    st.subheader("Sniper Settings")
    user_email = st.text_input("Club Email")
    user_pass = st.text_input("Club Password", type="password")
    start_time = st.time_input("Earliest Start", datetime.time(9, 0))
    end_time = st.time_input("Latest End", datetime.time(16, 0))
    
    if st.button("Save Preferences"):
        sb.table("sniper_prefs").upsert({
            "id": 1, 
            "email": user_email, 
            "min_time": str(start_time), 
            "max_time": str(end_time)
        }).execute()
        st.success("Preferences Saved")

# 5. SNIPER EXECUTION ENGINE
async def run_snipe_sequence():
    async with async_playwright() as p:
        # HEADLESS=TRUE and --no-sandbox are required for Cloud
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            st.info("Initiating Life Time Login...")
            await page.goto("https://www.lifetime.life/login", timeout=60000)
            
            # Login Sequence - Corrected Indentation
            await page.fill('input[name="username"]', user_email)
            await page.fill('input[name="password"]', user_pass)
            await page.click('button[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            st.info(f"Scanning for slots on {target_date}...")
            # Verification Screenshot
            await page.screenshot(path="confirmation.png")
            st.image("confirmation.png", caption="Current Portal View")
            st.success("Sniper sequence reached the portal successfully.")

        except Exception as e:
            st.error(f"Snipe Failed: {e}")
            await page.screenshot(path="error_state.png")
            st.image("error_state.png", caption="Error Context")
        finally:
            await browser.close()

# 6. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not user_email or not user_pass:
        st.error("Please enter credentials in the sidebar.")
    else:
        st.warning("Sniper Armed. Running sequence...")
        asyncio.run(run_snipe_sequence())
