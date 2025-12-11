import streamlit as st
import requests
import pandas as pd
import json

# --- CONFIGURATION ---
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" # Check your URL!

# --- PAGE CONFIG ---
st.set_page_config(page_title="Omni-Agent v2", page_icon="⚡", layout="wide")

# --- v2.0 LUXURY CSS ---
st.markdown("""
<style>
    /* 1. FORCE DARK THEME BACKGROUND */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* 2. GLASSMORPHISM CARDS */
    .metric-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s;
    }
    .metric-box:hover {
        transform: translateY(-5px);
        border-color: #00FF94;
    }
    .metric-box h3 {
        color: #888888 !important;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .metric-box h2 {
        color: #00FF94 !important; /* Neon Green */
        font-size: 32px;
        font-weight: 700;
        margin: 0;
    }
    
    /* 3. BUTTONS */
    .stButton>button {
        background: linear-gradient(45deg, #00C853, #009688);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 0 15px rgba(0, 255, 148, 0.4);
    }

    /* 4. HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_config" not in st.session_state:
    st.session_state.user_config = {}
if "orders" not in st.session_state:
    st.session_state.orders = []

# ==========================================
# 🔐 LOGIN SCREEN (v2.0)
# ==========================================
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<h1 style='text-align: center; color: white;'>⚡ OMNI-AGENT v2</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Enterprise AI for E-commerce</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("Access ID")
            password = st.text_input("Secret Key", type="password")
            submitted = st.form_submit_button("ENTER DASHBOARD")
            
            if submitted:
                # CHECK SECRETS
                try:
                    user_data = st.secrets["users"].get(username)
                    if user_data and user_data["password"] == password:
                        st.session_state.logged_in = True
                        st.session_state.user_config = user_data
                        st.rerun()
                    else:
                        st.error("⛔ Access Denied")
                except:
                    st.error("System Error: Check Secrets.")

# ==========================================
# ⚡ DASHBOARD (v2.0)
# ==========================================
else:
    # DATA LOADING
    client_name = st.session_state.user_config.get("name", "Client")
    saved_feed = st.session_state.user_config.get("feed_url", "")
    saved_webhook = st.session_state.user_config.get("webhook_url", "")
    saved_policy = st.session_state.user_config.get("policy", "Standard Policy")

    # HEADER
    c1, c2 = st.columns([6, 1])
    with c1:
        st.title(f"⚡ Command Center: {client_name}")
    with c2:
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # METRICS ROW
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-box"><h3>Revenue</h3><h2>${sum([o.get('quantity', 1) * 20 for o in st.session_state.orders])}</h2></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-box"><h3>Orders</h3><h2>{len(st.session_state.orders)}</h2></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-box"><h3>Feed Status</h3><h2 style="color:#00FF94 !important;">SYNCED</h2></div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""<div class="metric-box"><h3>AI Model</h3><h2>Llama 3</h2></div>""", unsafe_allow_html=True)

    st.markdown("###")

    # TABS
    tab1, tab2 = st.tabs(["💬 INSTAGRAM SIMULATOR", "⚙️ CONFIGURATION"])

    with tab1:
        st.caption("Test how the bot replies to Instagram DMs in real-time.")
        
        # Chat Interface
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Yo! Checking the inventory..."}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Type a DM (e.g., 'price for black hoodie?')..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("⚡ AI Thinking..."):
                try:
                    # LIVE FETCH
                    if saved_feed:
                        try:
                            df = pd.read_csv(saved_feed)
                            catalog_str = df.to_string(index=False)
                        except:
                            catalog_str = "Feed Error."
                    else:
                        catalog_str = "No Feed."

                    payload = {
                        "store_policy": saved_policy, 
                        "product_catalog": catalog_str,
                        "user_question": prompt
                    }
                    response = requests.post(WORKER_URL, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        raw = data.get("result", {}).get("response", "") or data.get("response", "")
                        clean = raw.replace("```json", "").replace("```", "").strip()
                        
                        try:
                            ai_action = json.loads(clean)
                            msg_text = ai_action.get("message", "Processed.")
                            
                            if ai_action.get("action") == "CREATE_ORDER":
                                st.success(f"🚀 ORDER SIGNAL SENT: {ai_action.get('item')}")
                                st.session_state.orders.append(ai_action)
                                if saved_webhook:
                                    requests.post(saved_webhook, json=ai_action)
                            
                            with st.chat_message("assistant"):
                                st.markdown(msg_text)
                            st.session_state.messages.append({"role": "assistant", "content": msg_text})
                        except:
                            st.error("AI Error.")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    with tab2:
        st.info("🔒 Secure Configuration (Managed by Admin)")
        st.text_input("Live Feed URL", value=saved_feed, disabled=True)
        st.text_input("Webhook URL", value=saved_webhook, disabled=True)
