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

# 2. SIDEBAR - ALL FEATURES RESTORED
with st.sidebar:
    st.subheader("📅 Target Settings")
    auto = st.toggle("8-Day Auto (9:00 AM Strike)", value=True)
    if auto:
        t_date = datetime.date.today() + datetime.timedelta(days=8)
    else:
        t_date = st.date_input("Date", datetime.date.today() + datetime.timedelta(days=8))

    st.subheader("🔑 Credentials")
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Start Time", datetime.time(17, 30))

st.title("🎾 Tennis Sniper Pro")
st.metric("Target Date", t_date.strftime("%A, %b %d"))

# 3. ENGINE - REINFORCED LOGIN
async def run_snipe(d, target_time):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Bypassing cookie banner...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # AGGRESSIVE BANNER BUSTER
            banner_sel = 'button:has-text("Accept All"), #onetrust-accept-btn-handler'
            try:
                await pg.wait_for_selector(banner_sel, timeout=10000)
                await pg.click(banner_sel)
                # Wait for the overlay to actually leave the DOM
                await pg.wait_for_selector(banner_sel, state="hidden", timeout=10000)
                st.success("Banner Destroyed ✅")
            except:
                st.write("No banner found, proceeding...")

            # LOGIN SEQUENCE (Now safe from overlays)
            st.info("Entering credentials...")
            e_sel, p_sel = 'input[type="email"], #username', 'input[type="password"], #password'
            await pg.wait_for_selector(e_sel, timeout=15000)
            await pg.fill(e_sel, u_em)
            await pg.fill(p_sel, u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION & SCROLLING
            st.info("Navigating to Grid...")
            url_base = "https://my.lifetime.life/clubs/ga/north-druid-hills/"
            url_file = "resource-booking.html?sport=Tennis%3A++Indoor+Court"
            url_tail = f"&clubId=232&date={d}&startTime=-1&duration=60&hideModal=true"
            await pg.goto(url_base + url_file + url_tail, timeout=60000)
            
            await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            await pg.screenshot(path="view.png", full_page=True)
            st.image("view.png", caption="Final Portal View")
            st.success("Target reached.")

        except Exception as err:
            st.error(f"Error: {err}")
            await pg.screenshot(path="err.png", full_page=True); st.image("err.png")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Enter credentials")
    else:
        asyncio.run(run_snipe(t_date, t_s))
