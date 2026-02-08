import streamlit as st
import asyncio, os, datetime
from playwright.async_api import async_playwright
from supabase import create_client

# 1. CLOUD SETUP
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    os.system("playwright install chromium --with-deps")

st.set_page_config(page_title="Tennis Sniper Pro", page_icon="🎾")

try:
    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Check Secrets"); st.stop()

# 2. SIDEBAR
with st.sidebar:
    st.subheader("📅 Target")
    club_options = {"North Druid Hills": "north-druid-hills", "Peachtree Corners": "peachtree-corners"}
    selected_club = st.selectbox("Club", list(club_options.keys()))
    
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Target Time", datetime.time(17, 30))

# 3. THE ENGINE (Login Focus)
async def run_snipe():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Landing on Login Page...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # STEP 1: FORCE CLEAR THE BANNER
            # We use a broad selector to find the 'Accept' button and click it first
            st.warning("Detecting Cookie Banner...")
            banner_button = pg.locator('button:has-text("Accept"), #onetrust-accept-btn-handler')
            if await banner_button.is_visible(timeout=5000):
                await banner_button.click()
                st.success("Banner Cleared! ✅")
            
            # STEP 2: LOGIN (Now that the path is clear)
            st.info("Entering Credentials...")
            await pg.fill('input[type="email"], #username', u_em)
            await pg.fill('input[type="password"], #password', u_pw)
            await pg.click('button[type="submit"]')
            
            # STEP 3: VERIFY LOGIN SUCCESS
            await pg.wait_for_load_state("networkidle")
            st.success("Login Successful! Landing on Dashboard.")
            
            await pg.screenshot(path="login_result.png")
            st.image("login_result.png", caption="Post-Login View")
            
        except Exception as err:
            st.error(f"Login Failed: {err}")
            await pg.screenshot(path="login_error.png")
            st.image("login_error.png", caption="What the Sniper sees right now")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Enter credentials")
    else:
        asyncio.run(run_snipe())
