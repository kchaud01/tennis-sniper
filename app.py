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
        t_date = st.date_input("Date", datetime.date.today() + datetime.timedelta(days=10))
    
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Start", datetime.time(17, 30))
    t_e = st.time_input("End", datetime.time(18, 30))

st.title("🎾 Tennis Sniper Pro")
st.metric("Target Date", t_date.strftime("%A, %b %d"))

# 3. ENGINE
async def run_snipe(d, s, e):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Logging in...")
            # Using the direct login portal URL
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # Updated Multi-Selectors for Life Time Login
            email_sel = 'input[type="email"], input[name="username"], #username'
            pass_sel = 'input[type="password"], input[name="password"], #password'
            
            await pg.wait_for_selector(email_sel, timeout=15000)
            await pg.fill(email_sel, u_em)
            await pg.fill(pass_sel, u_pw)
            await pg.click('button[type="submit"], #loginButton')
            
            await pg.wait_for_load_state("networkidle")
            st.success("Login Successful!")
            
            # This captures what the sniper sees after login
            await pg.screenshot(path="shot.png")
            st.image("shot.png", caption="Portal Dashboard")
            
        except Exception as err:
            st.error(f"Error: {err}")
            await pg.screenshot(path="err.png")
            st.image("err.png", caption="Error Screenshot")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Enter credentials")
    else:
        st.warning(f"Running for {t_date}...")
        asyncio.run(run_snipe(t_date, t_s, t_e))
