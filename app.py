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

# 2. SIDEBAR SETTINGS
with st.sidebar:
    st.subheader("📅 Target Settings")
    club_map = {
        "Peachtree Corners": "peachtree-corners/court-booking.html?clubId=232",
        "North Druid Hills": "north-druid-hills/court-booking.html?clubId=234"
    }
    selected_club = st.selectbox("Select Club", list(club_map.keys()))
    path_suffix = club_map[selected_club]
    
    auto = st.toggle("8-Day Auto", value=True)
    t_date = datetime.date.today() + datetime.timedelta(days=8) if auto else st.date_input("Date")
    
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Start", datetime.time(17, 30))
    t_e = st.time_input("End", datetime.time(18, 30))

st.title("🎾 Tennis Sniper Pro")
st.metric(f"Targeting {selected_club}", t_date.strftime("%A, %b %d"))

# 3. AUTOMATION ENGINE
async def run_snipe(d, suffix):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Clearing banners and logging in...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # BANNER BUSTER: Click "Accept All" immediately if it exists
            try:
                await pg.click('button:has-text("Accept All")', timeout=7000)
            except: pass 

            # LOGIN SEQUENCE
            email_sel = 'input[type="email"], input[name="username"], #username'
            pass_sel = 'input[type="password"], #password'
            
            await pg.wait_for_selector(email_sel, timeout=15000)
            await pg.fill(email_sel, u_em)
            await pg.fill(pass_sel, u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            st.info(f"Navigating to {selected_club} Schedule...")
            # Use the GA-specific club routing found in your history
            target_url = f"https://my.lifetime.life/clubs/ga/{suffix}&date={d}"
            await pg.goto(target_url, timeout=60000)
            await pg.wait_for_load_state("networkidle")
            
            # FINAL VERIFICATION
            await pg.screenshot(path="final_view.png")
            st.image("final_view.png", caption=f"Live Grid: {selected_club}")
            st.success("Correct grid located and cleared of popups!")
            
        except Exception as err:
            st.error(f"Error: {err}")
            await pg.screenshot(path="err.png"); st.image("err.png")
        finally:
            await b.close()

# 4. EXECUTION
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Enter credentials")
    else:
        st.warning(f"Sniper active for {selected_club}...")
        asyncio.run(run_snipe(t_date, path_suffix))
