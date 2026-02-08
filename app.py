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

# 2. SIDEBAR - ALL FUNCTIONALITY FULLY PRESERVED
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
st.metric(f"Targeting {sel_club}", t_date.strftime("%A, %b %d"))

# 3. ENGINE - REINFORCED LOGIN & ANCHOR STRIKE
async def run_snipe(d, c_slug, target_time):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Bypassing banner and logging in...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # CLEAR BANNER
            try:
                btn = pg.locator('button:has-text("Accept All"), #onetrust-accept-btn-handler')
                await btn.click(timeout=5000)
                await pg.wait_for_selector(btn, state="hidden", timeout=5000)
            except: pass

            # MULTI-SELECTOR LOGIN
            st.info("Entering credentials...")
            # We try multiple common selectors for the email field
            email_field = pg.locator('input[type="email"], #username, input[name="username"], [placeholder*="Email"]')
            await email_field.first.wait_for(state="visible", timeout=15000)
            await email_field.first.fill(u_em)
            
            pw_field = pg.locator('input[type="password"], #password, input[name="password"]')
            await pw_field.first.fill(u_pw)
            
            await pg.click('button[type="submit"], button:has-text("Log In")')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION
            st.info(f"Loading {sel_club} Grid...")
            time_str = target_time.strftime("%-I:%M %p") 
            url = f"https://my.lifetime.life/clubs/ga/{c_slug}/resource-booking.html"
            query = f"?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}"
            await pg.goto(url + query + "&startTime=-1&duration=60&hideModal=true")
            
            # STRIKE LOGIC: Using Anchor <a> tag from your Inspect data
            st.warning("Searching for " + time_str + "...")
            await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)

            # Using the <a> tag and .timeslot-time class you identified
            target_link = pg.locator('a[data-testid="resourceBookingTile"]').filter(
                has=pg.locator(".timeslot-time", has_text=time_str)
            ).first
            
            await target_link.wait_for(state="visible", timeout=15000)
            await target_link.click()
            st.success("Target slot clicked!")
            
            # FINAL CONFIRMATION
            confirm_btn = pg.locator('button:has-text("Reserve"), button:has-text("Confirm")')
            await confirm_btn.wait_for(state="visible", timeout=10000)
            await confirm_btn.click()
            st.success("✅ BOOKING COMPLETE!")

            await pg.screenshot(path="final.png", full_page=True)
            st.image("final.png")

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
        asyncio.run(run_snipe(t_date, slug, t_s))
