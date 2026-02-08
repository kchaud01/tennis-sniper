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

# 2. SIDEBAR SETTINGS
with st.sidebar:
    st.subheader("📅 Target Settings")
    club_options = {
        "North Druid Hills": "north-druid-hills",
        "Peachtree Corners": "peachtree-corners"
    }
    selected_club = st.selectbox("Select Club", list(club_options.keys()))
    club_slug = club_options[selected_club]
    
    auto = st.toggle("8-Day Auto (9:00 AM Strike)", value=True)
    t_date = datetime.date.today() + datetime.timedelta(days=8) if auto else st.date_input("Date")
    
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Target Start Time", datetime.time(17, 30))

st.title("🎾 Tennis Sniper Pro")
st.metric(f"Targeting {selected_club}", t_date.strftime("%A, %b %d"))

# 3. ENGINE
async def run_snipe(d, slug, target_time):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Clearing banners and logging in...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # BANNER BUSTER: Remove the cookie overlay immediately
            try:
                await pg.click('button:has-text("Accept All")', timeout=5000)
                st.write("Cookies Accepted ✅")
            except: pass 

            # LOGIN SEQUENCE
            e_sel = 'input[type="email"], input[name="username"], #username'
            p_sel = 'input[type="password"], #password'
            await pg.wait_for_selector(e_sel, timeout=15000)
            await pg.fill(e_sel, u_em)
            await pg.fill(p_sel, u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATE TO THE EXACT RESOURCE GRID
            st.info(f"Navigating to {selected_club} Resource Grid...")
            time_str = target_time.strftime("%I:%M %p").lstrip("0") 
            # Using your verified URL structure
            grid_url = f"https://my.lifetime.life/clubs/ga/{slug}/resource-booking.html?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}&startTime=-1&duration=60&hideModal=true"
            
            await pg.goto(grid_url, timeout=60000)
            await pg.wait_for_load_state("networkidle")
            
            # THE STRIKE
            st.warning(f"Searching for {time_str} slot...")
            slot_selector = f'button:has-text("{time_str}")'
            
            if await pg.query_selector(slot_selector):
                await pg.click(slot_selector)
                st.success(f"🎯 Slot {time_str} clicked!")
            else:
                st.error(f"Slot {time_str} not visible yet.")

            await pg.screenshot(path="final_view.png")
            st.image("final_view.png", caption="Live Portal View")
            
        except Exception as err:
            st.error(f"Error: {err}")
            await pg.screenshot(path="err.png"); st.image("err.png")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER / STRIKE NOW"):
    if not u_em or not u_pw:
        st.error("Enter credentials")
    else:
        st.warning(f"Sniper executing for {t_date}...")
        asyncio.run(run_snipe(t_date, club_slug, t_s))
