import streamlit as st
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

# 2. SIDEBAR - ALL FUNCTIONALITY RESTORED
with st.sidebar:
    st.subheader("📅 Target Settings")
    clubs = {"North Druid Hills": "north-druid-hills", "Peachtree Corners": "peachtree-corners"}
    sel_club = st.selectbox("Select Club", list(clubs.keys()))
    slug = clubs[sel_club]
    
    # RESTORED: Duration Selection
    dur = st.radio("Reservation Duration", [60, 90], index=0, horizontal=True)
    
    auto = st.toggle("8-Day Auto (9:00 AM Strike)", value=True)
    if auto:
        t_date = datetime.date.today() + datetime.timedelta(days=8)
    else:
        t_date = st.date_input("Date", datetime.date.today() + datetime.timedelta(days=8))

    st.subheader("🔑 Credentials")
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    
    st.subheader("⏰ Time Window")
    t_s = st.time_input("Target Time", datetime.time(16, 0))

st.title("🎾 Tennis Sniper Pro")
st.write(f"Targeting: {sel_club} ({dur} min) on {t_date.strftime('%A, %b %d')}")

# 3. ENGINE - REINFORCED FOR DURATION & MODALS
async def run_snipe(d, c_slug, target_time, duration):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        
        status = st.empty()
        try:
            status.info("Authenticating with Life Time...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # PRECISION LOGIN (Using id from your Inspect screenshot)
            await pg.wait_for_selector("#account-username", timeout=15000)
            await pg.fill("#account-username", u_em)
            await pg.fill('input[type="password"]', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION (Using RESTORED duration parameter)
            status.info(f"Loading {sel_club} Grid...")
            time_str = target_time.strftime("%-I:%M %p") 
            url = f"https://my.lifetime.life/clubs/ga/{c_slug}/resource-booking.html"
            # URL now dynamically handles duration
            query = f"?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}&startTime=-1&duration={duration}&hideModal=true"
            await pg.goto(url + query)
            await pg.wait_for_load_state("networkidle")
            
            # STRIKE LOGIC
            status.warning(f"Locating {time_
