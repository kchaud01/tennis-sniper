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

# 2. SIDEBAR - ZERO FUNCTIONALITY LOST
with st.sidebar:
    st.subheader("📅 Target Settings")
    clubs = {"North Druid Hills": "north-druid-hills", "Peachtree Corners": "peachtree-corners"}
    sel_club = st.selectbox("Select Club", list(clubs.keys()))
    slug = clubs[sel_club]
    
    auto = st.toggle("8-Day Auto (9:00 AM Strike)", value=True)
    if auto:
        t_date = datetime.date.today() + datetime.timedelta(days=8)
    else:
        t_date = st.date_input("Date", datetime.date.today() + datetime.timedelta(days=8))

    st.subheader("🔑 Credentials")
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Target Time", datetime.time(16, 0))

st.title("🎾 Tennis Sniper Pro")
st.write(f"Targeting: {sel_club} on {t_date.strftime('%A, %b %d')}")

# 3. ENGINE - REINFORCED FOR ONETRUST OVERLAYS
async def run_snipe(d, c_slug, target_time):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        
        # Use st.empty to ensure messages are cleared each run
        msg_area = st.empty()
        try:
            msg_area.info("Step 1: Navigating to Login...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # MODAL KILLER: Handles the "Confirm My Choices" shield from your error log
            msg_area.info("Step 2: Clearing OneTrust Barriers...")
            onetrust_btn = pg.locator('button:has-text("Confirm My Choices"), #onetrust-accept-btn-handler')
            try:
                await onetrust_btn.wait_for(state="visible", timeout=7000)
                await onetrust_btn.click()
                await asyncio.sleep(1) # Wait for fade-out
            except: pass

            # PRECISION LOGIN: Using id="account-username" from your Inspect screenshot
            msg_area.info("Step 3: Authenticating...")
            await pg.wait_for_selector("#account-username", timeout=15000)
            await pg.fill("#account-username", u_em)
            await pg.fill('input[type="password"]', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # VERIFY LOGIN SUCCESS
            if "login" in pg.url:
                raise Exception("Login failed - Check Credentials or Captcha")

            # GRID NAVIGATION
            msg_area.info("Step 4: Loading Court Grid...")
            time_str = target_time.strftime("%-I:%M %p") 
            url = f"https://my.lifetime.life/clubs/ga/{c_slug}/resource-booking.html"
            query = f"?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}"
            await pg.goto(url + query + "&startTime=-1&duration=60&hideModal=true")
            await pg.wait_for_load_state("networkidle")
            
            # STRIKE LOGIC: Using verified Anchor <a> tag logic
            msg_area.warning(f"Step 5: Striking {time_str} Slot...")
            await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            target_link = pg.locator('a[data-testid="resourceBookingTile"]').filter(
                has=pg.locator(".timeslot-time", has_text=time_str)
            ).first
            
            await target_link.wait_for(state="visible", timeout=15000)
            await target_link.click()
            
            # FINAL RESERVATION CONFIRMATION
            msg_area.info("Step 6: Finalizing Booking...")
            conf = pg.locator('button:has-text("Reserve"), button:has-text("Confirm")').last
            await conf.wait_for(state="visible", timeout=10000)
            await conf.click()
            
            msg_area.success(f"✅ FINALIZED: {time_str} Booked!")
            await pg.screenshot(path="final.png", full_page=True); st.image("final.png")

        except Exception as err:
            msg_area.error(f"Failed at Step: {err}")
            await pg.screenshot(path="err.png", full_page=True); st.image("err.png")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Please enter credentials in the sidebar.")
    else:
        asyncio.run(run_snipe(t_date, slug, t_s))
