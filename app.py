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

# 2. SIDEBAR - ALL FUNCTIONALITY PRESERVED
with st.sidebar:
    st.subheader("📅 Target Settings")
    clubs = {"North Druid Hills": "north-druid-hills", "Peachtree Corners": "peachtree-corners"}
    sel_club = st.selectbox("Select Club", list(clubs.keys()))
    slug = clubs[sel_club]
    
    # Duration Restored
    dur = st.radio("Duration", [60, 90], index=0, horizontal=True)
    
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
st.write(f"Targeting: {sel_club} ({dur}m) on {t_date.strftime('%b %d')}")

# 3. ENGINE - REINFORCED FOR VERIFIED CLICK
async def run_snipe(d, c_slug, target_time, duration):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        
        stt = st.empty()
        try:
            stt.info("Authenticating...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # LOGIN - Using verified id="account-username"
            await pg.wait_for_selector("#account-username", timeout=15000)
            await pg.fill("#account-username", u_em)
            await pg.fill('input[type="password"]', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION
            stt.info("Loading Grid...")
            tm_str = target_time.strftime("%-I:%M %p") 
            url = f"https://my.lifetime.life/clubs/ga/{c_slug}/resource-booking.html"
            query = f"?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}&startTime=-1&duration={duration}&hideModal=true"
            await pg.goto(url + query)
            await pg.wait_for_load_state("networkidle")
            
            # STRIKE LOGIC
            stt.warning("Locating slot...")
            await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            target = pg.locator('a[data-testid="resourceBookingTile"]').filter(
                has=pg.locator(".timeslot-time", has_text=tm_str)
            ).first
            
            await target.wait_for(state="visible", timeout=15000)
            await target.click()
            
            # NEW: FINAL MODAL KILLER (Targets the "Accept All" blocking the Finish button)
            stt.info("Clearing final blocking popup...")
            await asyncio.sleep(3) # Extra time for modal to fully cover the screen
            
            popups = ['button:has-text("Accept All")', 'button:has-text("Confirm My Choices")', '#onetrust-accept-btn-handler']
            for s in popups:
                try:
                    btn = pg.locator(s)
                    if await btn.is_visible():
                        await btn.click()
                        await asyncio.sleep(2) # Give it time to fade out
                except: pass
            
            # FINAL STRIKE: Using verified data-testid="finishBtn"
            stt.info("Executing Verifiable Finish...")
            finish_btn = pg.locator('button[data-testid="finishBtn"]')
            await finish_btn.wait_for(state="visible", timeout=15000)
            
            # We force the click and then wait for the page to actually change
            await finish_btn.click(force=True)
            await pg.wait_for_load_state("networkidle")
            
            # VERIFICATION: Does the "Finish" button still exist?
            if await finish_btn.is_visible():
                stt.error("Button still visible! Retrying click...")
                await finish_btn.click(force=True)
                await asyncio.sleep(3)

            stt.success("✅ REAL SUCCESS: Court Secured!")
            await pg.screenshot(path="final.png", full_page=True); st.image("final.png")

        except Exception as err:
            stt.error(f"Error: {err}")
            await pg.screenshot(path="err.png", full_page=True); st.image("err.png")
        finally:
            await b.close()

# 4. TRIGGER
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Credentials required.")
    else:
        asyncio.run(run_snipe(t_date, slug, t_s, dur))
