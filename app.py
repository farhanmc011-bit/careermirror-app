import streamlit as st
import requests
import pandas as pd
import json
import re
from datetime import datetime

# --- ⚙️ CONFIGURATION ---
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" 

# --- 🎨 PAGE CONFIG & STRIPE-STYLE CSS ---
st.set_page_config(page_title="Client Portal", page_icon="✨", layout="wide")

st.markdown("""
<style>
    /* 1. FORCE CLEAN WHITE BACKGROUND */
    .stApp {
        background-color: #FFFFFF;
        color: #1A1A1A;
    }

    /* 2. TYPOGRAPHY (Inter / System Font) */
    h1, h2, h3, h4, h5, h6, p, label, li, span, div {
        color: #1A1A1A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* 3. FIX THE CODE BLOCK (The problem you saw) */
    /* We make it look like a clean documentation snippet (Light Grey) */
    .stCodeBlock {
        background-color: #F3F4F6 !important; /* Light Grey Bg */
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }
    code {
        color: #111827 !important; /* Dark Text for readability */
        font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
        background-color: transparent !important;
    }
    
    /* 4. SIDEBAR - SOFT GRAY */
    section[data-testid="stSidebar"] {
        background-color: #F9FAFB;
        border-right: 1px solid #E5E7EB;
    }
    
    /* 5. METRIC CARDS (Stripe Style) */
    .metric-card {
        background: #FFFFFF;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: box-shadow 0.2s;
    }
    .metric-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .metric-card h3 { 
        color: #6B7280 !important;
        font-size: 12px !important; 
        text-transform: uppercase; 
        font-weight: 600; 
        margin-bottom: 8px; 
        letter-spacing: 0.5px;
    }
    .metric-card h2 { 
        color: #111827 !important;
        font-size: 30px !important; 
        font-weight: 700; 
        margin: 0; 
    }
    
    /* 6. BUTTONS (Black & Sharp) */
    .stButton>button {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 500;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        background-color: #000000 !important;
    }

    /* 7. INPUTS (Clean Borders) */
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
    }
    .stTextInput input:focus {
        border-color: #111827;
        box-shadow: none;
    }

    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 📦 SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_config" not in st.session_state: st.session_state.user_config = {}
if "orders" not in st.session_state: st.session_state.orders = []
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "System Online. Ready."}]

# ==========================================
# 🔐 LOGIN SCREEN
# ==========================================
def login_page():
    c1, c2, c3 = st.columns([1, 0.6, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; margin-bottom: 0px;'>Client Portal</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280; font-size: 14px;'>Enterprise Access</p>", unsafe_allow_html=True)
        
        with st.form("login", border=False):
            username = st.text_input("ID")
            password = st.text_input("Key", type="password")
            submitted = st.form_submit_button("Authenticate", use_container_width=True)
            
            if submitted:
                # Basic cleaner
                u = username.strip()
                p = password.strip()
                try:
                    user = st.secrets["users"].get(u)
                    if user and str(user["password"]) == str(p):
                        st.session_state.logged_in = True
                        st.session_state.user_config = user
                        st.rerun()
                    else:
                        st.error("Access Denied")
                except:
                    st.error("System Error")

# ==========================================
# 🖥️ DASHBOARD
# ==========================================
def main_app():
    # SIDEBAR
    with st.sidebar:
        st.markdown("### Nexus AI")
        st.caption(f"Account: {st.session_state.user_config.get('name')}")
        st.markdown("---")
        menu = st.radio("Menu", ["Dashboard", "Live Simulator", "Orders", "Installation"], label_visibility="collapsed")
        st.markdown("---")
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.rerun()

    # VIEW 1: DASHBOARD
    if menu == "Dashboard":
        st.title("Overview")
        st.markdown("<br>", unsafe_allow_html=True)
        
        rev = sum([o.get('quantity', 1) * 20 for o in st.session_state.orders])
        count = len(st.session_state.orders)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"""<div class="metric-card"><h3>Revenue</h3><h2>${rev}</h2></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="metric-card"><h3>Orders</h3><h2>{count}</h2></div>""", unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class="metric-card"><h3>Sync Status</h3><h2 style="color:#10B981 !important;">Live</h2></div>""", unsafe_allow_html=True)
        with c4: st.markdown(f"""<div class="metric-card"><h3>Model</h3><h2>v2.0</h2></div>""", unsafe_allow_html=True)
        
        st.markdown("###")
        st.caption("Recent Activity Log")
        if count > 0:
             # Simple List
             for o in st.session_state.orders[-5:]:
                 st.info(f"💰 {o.get('date', 'Just now')} - {o.get('item')} sold")
        else:
            st.info("No activity recorded yet.")

    # VIEW 2: SIMULATOR
    elif menu == "Live Simulator":
        st.title("Simulator")
        
        for msg in st.session_state.messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

        if prompt := st.chat_input("Test your bot..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()
                placeholder.markdown("...")
                try:
                    cfg = st.session_state.user_config
                    payload = {
                        "store_policy": cfg.get("policy", "Standard"),
                        "product_catalog": "", # The worker uses the feed_url internally if needed, or we fetch here.
                        "user_question": prompt
                    }
                    # We pass the feed URL in the prompt for v1 worker, OR if using v2 worker:
                    # Let's assume v2 worker handles it. 
                    # For RAG, we don't send catalog. For v1/v2 simple, we send it.
                    # FIX: If using v2 simple worker, we need to fetch the Atom feed text here.
                    # But to keep it simple and robust:
                    res = requests.post(WORKER_URL, json=payload)
                    
                    if res.status_code == 200:
                        data = res.json()
                        raw = data.get("result", {}).get("response", "") or data.get("response", "") or str(data)
                        match = re.search(r'\{.*\}', raw, re.DOTALL)
                        if match:
                            action = json.loads(match.group(0))
                            txt = action.get("message", "Done")
                            if action.get("action") == "CREATE_ORDER":
                                st.toast(f"Order: {action.get('item')}")
                                action["date"] = datetime.now().strftime("%H:%M")
                                st.session_state.orders.append(action)
                            placeholder.write(txt)
                            st.session_state.messages.append({"role": "assistant", "content": txt})
                        else:
                            placeholder.write(raw)
                except:
                    placeholder.error("Connection Error")

    # VIEW 3: ORDERS
    elif menu == "Orders":
        st.title("Orders")
        if st.session_state.orders:
            st.dataframe(pd.DataFrame(st.session_state.orders), use_container_width=True)
        else:
            st.info("No orders found.")

    # VIEW 4: INSTALLATION (FIXED VISIBILITY)
    elif menu == "Installation":
        st.title("Installation")
        st.markdown("Copy the code below.")
        
        code_snippet = f"""<script>
  window.BOT_CONFIG = {{
    workerUrl: "{WORKER_URL}",
    policy: "Standard"
  }};
</script>
<script src="https://cdn.jsdelivr.net/gh/farhanmc011/chat-widget@main/widget.js" async></script>"""

        # This will now appear in a LIGHT GREY box with DARK TEXT
        st.code(code_snippet, language="html")
        
        st.success("✅ Widget is ready to deploy.")

if st.session_state.logged_in:
    main_app()
else:
    login_page()
