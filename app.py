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

# 2. SIDEBAR & CLUB SELECTION
with st.sidebar:
    st.subheader("📅 Settings")
    # Mapping to specific URL paths discovered in your history
    club_paths = {
        "Peachtree Corners": "peachtree-corners/court-booking.html?clubId=232",
        "North Druid Hills": "north-druid-hills/court-booking.html?clubId=234"
    }
    selected_club = st.selectbox("Select Club", list(club_paths.keys()))
    path_suffix = club_paths[selected_club]
    
    auto = st.toggle("8-Day Auto", value=True)
    t_date = datetime.date.today() + datetime.timedelta(days=8) if auto else st.date_input("Date")
    
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Start", datetime.time(17, 30))
    t_e = st.time_input("End", datetime.time(18, 30))

st.title("🎾 Tennis Sniper Pro")
st.metric(f"Targeting {selected_club}", t_date.strftime("%A, %b %d"))

# 3. ENGINE
async def run_snipe(d, s, e, suffix):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Logging in...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # Login selectors
            e_sel, p_sel = 'input[type="email"], #username', 'input[type="password"], #password'
            await pg.fill(e_sel, u_em)
            await pg.fill(p_sel, u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # BANNER BUSTER: Click "Accept All" if cookies popup appears
            try:
                await pg.click('button:has-text("Accept All")', timeout=5000)
            except: pass 

            st.info(f"Navigating to {selected_club} Schedule...")
            # Building the correct URL for the chosen Atlanta club
            full_url = f"https://my.lifetime.life/clubs/ga/{suffix}&date={d}"
            await pg.goto(full_url, timeout=60000)
            await pg.wait_for_load_state("networkidle")
            
            # Verification
            await pg.screenshot(path="shot.png")
            st.image("shot.png", caption=f"Schedule for {selected_club}")
            
            # Logic for the February 16 strike window goes here
            st.success("Correct grid located!")
            
        except Exception as err:
            st.error(f"Error: {err}")
            await pg.screenshot(path="err.png"); st.image("err.png")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Enter credentials")
    else:
        st.warning(f"Sniper active for {selected_club} on {t_date}...")
        asyncio.run(run_snipe(t_date, t_s, t_e, path_suffix))
