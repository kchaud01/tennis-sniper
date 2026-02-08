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
    # Club IDs for your preferred Atlanta locations
    club_map = {"Peachtree Corners": "232", "North Druid Hills": "234"}
    selected_club = st.selectbox("Select Club", list(club_map.keys()))
    cid = club_map[selected_club]
    
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
st.metric(f"Targeting {selected_club}", t_date.strftime("%A, %b %d"))

# 3. ENGINE
async def run_snipe(d, s, e, club_id):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Logging in...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # Login
            e_sel = 'input[type="email"], input[name="username"], #username'
            p_sel = 'input[type="password"], input[name="password"], #password'
            await pg.fill(e_sel, u_em)
            await pg.fill(p_sel, u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            st.info(f"Navigating to {selected_club} Schedule...")
            # Direct link to the booking grid for your specific club and date
            grid_url = f"https://my.lifetime.life/clubs/ga/{selected_club.lower().replace(' ', '-')}/court-booking.html?date={d}&clubId={club_id}"
            await pg.goto(grid_url, timeout=60000)
            await pg.wait_for_load_state("networkidle")
            
            st.success(f"Grid Loaded for {selected_club}!")
            await pg.screenshot(path="shot.png")
            st.image("shot.png", caption=f"Schedule for {d}")
            
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
        asyncio.run(run_snipe(t_date, t_s, t_e, cid))
