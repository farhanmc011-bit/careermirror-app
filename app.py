import streamlit as st
import requests
import pandas as pd
import json
import re # Added for smart searching

# --- CONFIGURATION ---
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" 

# --- PAGE CONFIG ---
st.set_page_config(page_title="Omni-Agent v2", page_icon="⚡", layout="wide")

# --- v2.0 LUXURY CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .metric-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-box h3 { color: #888888 !important; font-size: 14px; margin-bottom: 5px; }
    .metric-box h2 { color: #00FF94 !important; font-size: 32px; font-weight: 700; margin: 0; }
    .stButton>button {
        background: linear-gradient(45deg, #00C853, #009688);
        color: white; border: none; border-radius: 8px; font-weight: bold;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_config" not in st.session_state: st.session_state.user_config = {}
if "orders" not in st.session_state: st.session_state.orders = []

# ==========================================
# 🔐 LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<h1 style='text-align: center; color: white;'>⚡ OMNI-AGENT v2</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Access ID")
            password = st.text_input("Secret Key", type="password")
            if st.form_submit_button("ENTER DASHBOARD"):
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
# ⚡ DASHBOARD
# ==========================================
else:
    client_name = st.session_state.user_config.get("name", "Client")
    saved_feed = st.session_state.user_config.get("feed_url", "")
    saved_webhook = st.session_state.user_config.get("webhook_url", "")
    saved_policy = st.session_state.user_config.get("policy", "Standard Policy")

    # HEADER
    c1, c2 = st.columns([6, 1])
    with c1: st.title(f"⚡ Command Center: {client_name}")
    with c2:
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # METRICS
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.markdown(f"""<div class="metric-box"><h3>Revenue</h3><h2>${sum([o.get('quantity', 1) * 20 for o in st.session_state.orders])}</h2></div>""", unsafe_allow_html=True)
    with m2: st.markdown(f"""<div class="metric-box"><h3>Orders</h3><h2>{len(st.session_state.orders)}</h2></div>""", unsafe_allow_html=True)
    with m3: st.markdown(f"""<div class="metric-box"><h3>Feed Status</h3><h2 style="color:#00FF94 !important;">SYNCED</h2></div>""", unsafe_allow_html=True)
    with m4: st.markdown(f"""<div class="metric-box"><h3>AI Model</h3><h2>Llama 3</h2></div>""", unsafe_allow_html=True)

    st.markdown("###")

    # CHAT TAB
    st.caption("Test how the bot replies to Instagram DMs in real-time.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Yo! Checking the inventory..."}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type a DM..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("⚡ AI Thinking..."):
            try:
                # FETCH DATA
                catalog_str = "No Feed."
                if saved_feed:
                    try:
                        df = pd.read_csv(saved_feed)
                        catalog_str = df.to_string(index=False)
                    except: pass

                payload = { "store_policy": saved_policy, "product_catalog": catalog_str, "user_question": prompt }
                response = requests.post(WORKER_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    # 🔴 SMART PARSING LOGIC 🔴
                    raw_text = data.get("result", {}).get("response", "") or data.get("response", "") or str(data)
                    
                    # Regex: Find the first thing that looks like { ... }
                    json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                    
                    if json_match:
                        clean_json = json_match.group(0)
                        try:
                            ai_action = json.loads(clean_json)
                            msg_text = ai_action.get("message", "Processed.")
                            
                            if ai_action.get("action") == "CREATE_ORDER":
                                st.success(f"🚀 ORDER SIGNAL SENT: {ai_action.get('item')}")
                                st.session_state.orders.append(ai_action)
                                if saved_webhook: requests.post(saved_webhook, json=ai_action)
                            
                            with st.chat_message("assistant"): st.markdown(msg_text)
                            st.session_state.messages.append({"role": "assistant", "content": msg_text})
                        except: st.error(f"JSON Parse Error: {raw_text}")
                    else:
                        st.error(f"AI failed to produce JSON. Raw: {raw_text}")
                else:
                    st.error("Server Error")
            except Exception as e:
                st.error(f"Connection Error: {e}")
