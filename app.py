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

# 2. SIDEBAR - ALL FEATURES PRESERVED
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

# 3. ENGINE - REINFORCED FOR VISIBILITY ISSUES
async def run_snipe(d, target_time):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Landing on login page...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # BANNER BUSTER
            banner_sel = 'button:has-text("Accept All"), #onetrust-accept-btn-handler'
            try:
                await pg.wait_for_selector(banner_sel, timeout=7000)
                await pg.click(banner_sel)
                await asyncio.sleep(2) # Wait for animation to finish
                st.success("Banner Dismissed ✅")
            except:
                pass

            # NEW: FORCE WAIT FOR FORM VISIBILITY
            st.info("Waiting for login form to become interactive...")
            e_sel = 'input[type="email"], #username, input[name="username"]'
            # Use 'attached' state first to ensure it's in the DOM
            await pg.wait_for_selector(e_sel, state="attached", timeout=20000)
            
            # If a loading spinner is present, wait for it to disappear
            try: await pg.wait_for_selector(".loading, .spinner", state="hidden", timeout=5000)
            except: pass

            await pg.fill(e_sel, u_em)
            await pg.fill('input[type="password"], #password', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION & SCROLLING
            st.info("Navigating to Schedule...")
            url_path = f"north-druid-hills/resource-booking.html?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}"
            await pg.goto(f"https://my.lifetime.life/clubs/ga/{url_path}&startTime=-1&duration=60&hideModal=true")
            
            # Force scroll to reveal 17:30 slots
            await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            await pg.screenshot(path="view.png", full_page=True)
            st.image("view.png", caption="Live Grid View")
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
