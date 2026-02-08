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
    clubs = {"North Druid Hills": "north-druid-hills", "Peachtree Corners": "peachtree-corners"}
    sel_club = st.selectbox("Select Club", list(clubs.keys()))
    slug = clubs[sel_club]
    
    auto = st.toggle("8-Day Auto (9:00 AM Strike)", value=True)
    t_date = datetime.date.today() + datetime.timedelta(days=8) if auto else st.date_input("Date")

    st.subheader("🔑 Credentials")
    u_em = st.text_input("Email", value="kchaudhuri@gmail.com")
    u_pw = st.text_input("Password", type="password")
    t_s = st.time_input("Target Time", datetime.time(16, 0))

st.title("🎾 Tennis Sniper Pro")
st.metric(f"Targeting {sel_club}", t_date.strftime("%A, %b %d"))

# 3. THE SNIPER ENGINE
async def run_snipe(d, c_slug, target_time):
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True, args=['--no-sandbox'])
        pg = await b.new_page()
        try:
            st.info("Bypassing banner and logging in...")
            await pg.goto("https://my.lifetime.life/login", timeout=60000)
            
            # BANNER BUSTER
            try:
                btn = pg.locator('button:has-text("Accept All"), #onetrust-accept-btn-handler')
                await btn.click(timeout=5000)
                await pg.wait_for_selector('button:has-text("Accept All")', state="hidden")
            except: pass

            # LOGIN
            await pg.fill('input[type="email"], #username', u_em)
            await pg.fill('input[type="password"], #password', u_pw)
            await pg.click('button[type="submit"]')
            await pg.wait_for_load_state("networkidle")
            
            # NAVIGATION
            st.info(f"Navigating to {sel_club} Grid...")
            time_str = target_time.strftime("%I:%M %p").lstrip("0") 
            url = f"https://my.lifetime.life/clubs/ga/{c_slug}/resource-booking.html"
            query = f"?sport=Tennis%3A++Indoor+Court&clubId=232&date={d}"
            await pg.goto(url + query + "&startTime=-1&duration=60&hideModal=true")
            await pg.wait_for_load_state("networkidle")
            
            # FORCE SCROLL & FIND
            st.warning(f"Waiting for {time_str} slot...")
            slot_sel = f'button:has-text("{time_str}")'
            
            # Loop to handle slow rendering/lazy loading
            found = False
            for i in range(5):
                await pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1) # wait for render
                if await pg.locator(slot_sel).first.is_visible():
                    found = True
                    break
            
            if found:
                slot = pg.locator(slot_sel).first
                await slot.scroll_into_view_if_needed()
                await slot.click()
                st.success(f"🎯 Slot {time_str} clicked!")
                
                # FINAL CONFIRMATION
                confirm_btn = pg.locator('button:has-text("Reserve"), button:has-text("Confirm")')
                await confirm_btn.wait_for(state="visible", timeout=10000)
                await confirm_btn.click()
                st.success("✅ BOOKING COMPLETE!")
            else:
                st.error(f"Slot {time_str} not detected after force-scrolling.")

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
