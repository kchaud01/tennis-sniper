import streamlit as st
import asyncio, os, datetime
from playwright.async_api import async_playwright
from supabase import create_client

# 1. SETUP
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    os.system("playwright install chromium --with-deps")

st.set_page_config(page_title="Tennis Sniper Pro", page_icon="🎾")

try:
    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Check Secrets"); st.stop()

# 2. SIDEBAR
with st.sidebar:
    st.subheader("📅 Settings")
    auto = st.toggle("8-Day Auto", value=True)
    if auto:
        t_date = datetime.date.today() + datetime.timedelta(days=8)
    else:
        t_date = st.date_input("Date", datetime.date.today() + datetime.timedelta(days=8))
    
    u_em = st.text_input("Email")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Start", datetime.time(9, 0))
    t_e = st.time_input("End", datetime.time(16, 0))

st.title("🎾 Tennis Sniper Pro")
st.metric("Target Date", t_date.strftime("%A, %b %d"))

# 3. ENGINE
async def run_snipe(d, s, e):
    async with async_playwright() as p:
        # Cloud-specific launch
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Logging in...")
            url = "https://www.lifetime.life/login"
            await pg.goto(url, timeout=60000)
            
            # Short-line inputs to prevent truncation errors
            await pg.fill('input[name="username"]', u_em)
            await pg.fill('input[name="password"]', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            st.success("Portal Loaded")
            await pg.screenshot(path="shot.png")
            st.image("shot.png")
        except Exception as err:
            st.error(f"Error: {err}")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Enter credentials")
    else:
        st.warning(f"Running for {t_date}...")
        asyncio.run(run_snipe(t_date, t_s, t_e))
