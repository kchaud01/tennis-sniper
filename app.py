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

# 2. SIDEBAR - ALL FUNCTIONALITY RESTORED & PROTECTED
with st.sidebar:
    st.subheader("📅 Target Settings")
    
    # Club Selection (Preserved)
    clubs = {"North Druid Hills": "north-druid-hills", "Peachtree Corners": "peachtree-corners"}
    sel_club = st.selectbox("Select Club", list(clubs.keys()))
    slug = clubs[sel_club]
    
    # Duration Selection (Preserved)
    dur = st.radio("Reservation Duration", [60, 90], index=0, horizontal=True)
    
    # 8-Day vs Manual Toggle (Preserved)
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

# 3. ENGINE - REINFORCED FOR DURATION & POPUPS
async def run_snipe(d, c_slug, target_time, duration):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        
        # We use a status object to keep you informed without stale messages
        st_msg = st.empty()
        try:
            st_msg.info("Step 1: Logging into Life Time...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # LOGIN - Using precision ID from your Inspect screenshot
            await pg.wait_for_selector("#account-username", timeout=15000)
            await pg.fill("#account-username", u_em)
            await pg.fill('input[type="password"]', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION (Using the duration choice)
            st_msg.info(f"Step 2: Loading {duration}m Grid for {sel_club}...")
            time_str = target_time.strftime("%-I:%M %p") 
            url = f"https://my.lifetime.life/clubs/ga/{c_slug}/resource-booking.html"
            query = f"?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}&startTime=-1&duration={duration}&hideModal=true"
            await pg.goto(url + query)
            await pg.wait_for_load_state("networkidle")
            
            # STRIKE LOGIC
            st_msg.warning(f"Step 3: Striking {time_str} slot...")
            await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            # Targeted Anchor Selector from your diagnostic
            target_link = pg.locator('a[data-testid="resourceBookingTile"]').filter(
                has=pg.locator(".timeslot-time", has_text=time_str)
            ).first
            
            await target_link.wait_for(state="visible", timeout=15000)
            await target_link.click()
            
            # MODAL KILLER (Handles the "Confirm My Choices" and "Accept All" popups)
            st_msg.info("Step 4: Clearing final popups...")
            await asyncio.sleep(2)
            
            popups = ['button:has-text("Accept All")', 'button:has-text("Confirm My Choices")', '#onetrust-accept-btn-handler']
            for selector in popups:
                try:
                    p_btn = pg.locator(selector)
                    if await p_btn.is_visible():
                        await p_btn.click()
                        await asyncio.sleep(1)
                except: pass
            
            # FINAL CONFIRMATION
            st_msg.info("Step 5: Finalizing Reservation...")
            res_btn = pg.locator('button:has-text("Reserve"), button:has-text("Confirm")').last
            await res_btn.wait_for(state="visible", timeout=10000)
            await res_btn.click()
            
            st_msg.success(f"✅ SUCCESS: {time_str} ({duration}m) Booked!")
            await pg.screenshot(path="final.png", full_page=True); st.image("final.png")

        except Exception as err:
            st_msg.error(f"Failed: {err}")
            await pg.screenshot(path="err.png", full_page=True); st.image("err.png")
        finally:
            await b.close()

# 4. TRIGGER - VERIFIED PARENTHESES
if st.button("🎯 ARM SNIPER"):
    if not u_em or not u_pw:
        st.error("Credentials required.")
    else:
        asyncio.run(run_snipe(t_date, slug, t_s, dur))
