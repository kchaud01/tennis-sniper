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

# 2. SIDEBAR - RESTORED CLUB CHOICE & DATE LOGIC
with st.sidebar:
    st.subheader("📅 Target Settings")
    
    # RESTORED: Club selection dropdown
    club_options = {
        "North Druid Hills": "north-druid-hills",
        "Peachtree Corners": "peachtree-corners"
    }
    selected_club = st.selectbox("Select Club", list(club_options.keys()))
    club_slug = club_options[selected_club]
    
    # RESTORED: 8-Day vs Manual Toggle
    auto = st.toggle("8-Day Auto (9:00 AM Strike)", value=True)
    if auto:
        t_date = datetime.date.today() + datetime.timedelta(days=8)
    else:
        t_date = st.date_input("Manual Date", datetime.date.today() + datetime.timedelta(days=8))

    st.subheader("🔑 Credentials")
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    
    st.subheader("⏰ Time Window")
    t_s = st.time_input("Start Time", datetime.time(17, 30))

st.title("🎾 Tennis Sniper Pro")
st.metric(f"Targeting {selected_club}", t_date.strftime("%A, %b %d"))

# 3. ENGINE - REINFORCED FOR LOGIN & SCROLLING
async def run_snipe(d, slug, target_time):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Clearing banner and logging in...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # BANNER BUSTER
            try:
                banner = pg.locator('button:has-text("Accept All"), #onetrust-accept-btn-handler')
                await banner.click(timeout=5000)
                st.success("Banner Dismissed ✅")
            except: pass

            # LOGIN
            await pg.fill('input[type="email"], #username', u_em)
            await pg.fill('input[type="password"], #password', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION - USING THE NORTH DRUID HILLS PATH
            st.info(f"Loading {selected_club} Schedule...")
            url = f"https://my.lifetime.life/clubs/ga/{slug}/resource-booking.html?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}&startTime=-1&duration=60&hideModal=true"
            
            await pg.goto(url, timeout=60000)
            await pg.wait_for_load_state("networkidle")
            
            # AUTO-SCROLL to find evening slots
            await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            
            await pg.screenshot(path="view.png", full_page=True)
            st.image("view.png", caption=f"Live Grid for {selected_club}")
            st.success("Correct grid located!")

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
        asyncio.run(run_snipe(t_date, club_slug, t_s))
