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
    
    # Restored Club Selection
    club_options = {
        "North Druid Hills": "north-druid-hills",
        "Peachtree Corners": "peachtree-corners"
    }
    selected_club = st.selectbox("Select Club", list(club_options.keys()))
    club_slug = club_options[selected_club]

    # Restored 8-Day vs Manual Toggle
    auto = st.toggle("8-Day Auto (9:00 AM Strike)", value=True)
    if auto:
        t_date = datetime.date.today() + datetime.timedelta(days=8)
    else:
        t_date = st.date_input("Date", datetime.date.today() + datetime.timedelta(days=8))

    st.subheader("🔑 Credentials")
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    
    st.subheader("⏰ Time Window")
    t_s = st.time_input("Start Time", datetime.time(17, 30))

st.title("🎾 Tennis Sniper Pro")
st.metric(f"Targeting {selected_club}", t_date.strftime("%A, %b %d"))

# 3. ENGINE - REINFORCED LOGIN
async def run_snipe(d, slug, target_time):
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
            e_sel = 'input[type="email"], #username, input[name="username"]'
            p_sel = 'input[type="password"], #password'
            
            await pg.wait_for_selector(e_sel, timeout=15000)
            await pg.fill(e_sel, u_em)
            await pg.fill(p_sel, u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION & SCROLLING
            st.info(f"Navigating to {selected_club} Grid...")
            url_base = f"https://my.lifetime.life/clubs/ga/{slug}/"
            url_file = "resource-booking.html?sport=Tennis%3A++Indoor+Court"
            url_tail = f"&clubId=232&date={d}&startTime=-1&duration=60&hideModal=true"
            
            await pg
