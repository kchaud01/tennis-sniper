\import streamlit as st
import asyncio, os, datetime
from playwright.async_api import async_playwright
from supabase import create_client

# 1. CLOUD BROWSER SETUP
if not os.path.exists("/home/appuser/.cache/ms-playwright"):
    os.system("playwright install chromium --with-deps")

st.set_page_config(page_title="Tennis Sniper Pro", page_icon="🎾")

try:
    sb = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
except:
    st.error("Check Secrets"); st.stop()

# 2. SIDEBAR - RESTORED FUNCTIONALITY
with st.sidebar:
    st.subheader("📅 Target Settings")
    
    # Restored the 8-Day Toggle
    auto = st.toggle("8-Day Auto (9:00 AM Strike)", value=True)
    
    # Restored the Calendar/Date Logic
    if auto:
        t_date = datetime.date.today() + datetime.timedelta(days=8)
        st.info(f"Auto-targeting: {t_date.strftime('%A, %b %d')}")
    else:
        t_date = st.date_input("Select Manual Date", datetime.date.today() + datetime.timedelta(days=8))

    st.subheader("🔑 Credentials")
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    
    st.subheader("⏰ Time Window")
    t_s = st.time_input("Target Start Time", datetime.time(17, 30))

st.title("🎾 Tennis Sniper Pro")
st.metric("Target Date", t_date.strftime("%A, %b %d"))

# 3. ENGINE - REINFORCED LOGIN & SCROLLING
async def run_snipe(d, target_time):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Attempting to bypass login banner...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # BANNER BUSTER: Specifically targeting that 'Accept All' overlay from your screenshots
            try:
                banner_button = pg.locator('button:has-text("Accept All"), #onetrust-accept-btn-handler')
                await banner_button.click(timeout=5000)
                st.success("Cookie Banner Dismissed ✅")
            except:
                st.write("No banner detected, proceeding...")

            # LOGIN SEQUENCE
            await pg.fill('input[type="email"], #username', u_em)
            await pg.fill('input[type="password"], #password', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # SCROLLING LOGIC
            st.info("Navigating to Schedule & Scrolling...")
            # Using the North Druid Hills URL we verified earlier
            grid_url = f"https://my.lifetime.life/clubs/ga/north-druid-hills/resource-booking.html?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}&startTime=-1&duration=60&hideModal=true"
            await pg.goto(grid_url, timeout=60000)
            
            # Auto-scroll to ensure evening slots render
            await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            await pg.screenshot(path="final_view.png", full_page=True)
            st.image("final_view.png", caption="Full Portal View")
            st.success("Navigation Complete.")

        except Exception as err:
            st.error(f"Error: {err}")
            await pg.screenshot(path="error.png", full_page=True); st.image("error.png")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Enter credentials")
    else:
        asyncio.run(run_snipe(t_date, t_s))
