import streamlit as st
import requests
import pandas as pd
import json

# --- CONFIGURATION ---
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" 

# --- PAGE CONFIG ---
st.set_page_config(page_title="Omni-Agent Login", page_icon="🔒", layout="centered")

# --- CSS FOR LOGIN & DASHBOARD ---
st.markdown("""
<style>
    .metric-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00cc66;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-box h3 { color: #666666 !important; margin: 0; font-size: 16px; }
    .metric-box h2 { color: #000000 !important; margin: 0; font-size: 28px; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    /* Hide Streamlit Menu for Clients */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
# 🔐 1. THE LOGIN SCREEN
# ==========================================
if not st.session_state.logged_in:
    st.title("🔒 Client Portal")
    st.caption("Please log in to manage your AI Agent.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")
        
        if submitted:
            # CHECK CREDENTIALS FROM SECRETS (The Concierge DB)
            try:
                # Look for the user in the secrets file
                user_data = st.secrets["users"].get(username)
                
                if user_data and user_data["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_config = user_data
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
            except Exception as e:
                st.error("System Error: Setup Secrets first.")
    
    st.info("Need an account? Contact Support to set up your Agent.")

# ==========================================
# 🛍️ 2. THE CLIENT DASHBOARD (PROTECTED)
# ==========================================
else:
    # Switch Layout to Wide for Dashboard
    # (Streamlit doesn't allow dynamic layout change easily, so we just use full width containers)
    
    # LOAD CLIENT'S SAVED DATA (The Persistence!)
    client_name = st.session_state.user_config.get("name", "Store Owner")
    saved_feed = st.session_state.user_config.get("feed_url", "")
    saved_webhook = st.session_state.user_config.get("webhook_url", "")
    saved_policy = st.session_state.user_config.get("policy", "Standard Policy")

    # --- HEADER ---
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title(f"👋 Welcome, {client_name}")
    with c2:
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- METRICS ---
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""<div class="metric-box"><h3>💰 Sales</h3><h2>${sum([o.get('quantity', 1) * 20 for o in st.session_state.orders])}</h2></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-box"><h3>📦 Orders</h3><h2>{len(st.session_state.orders)}</h2></div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-box"><h3>⚡ Feed Status</h3><h2 style="color:green !important;">Active</h2></div>""", unsafe_allow_html=True)

    st.markdown("###")

    # --- TABS ---
    tab_sim, tab_settings = st.tabs(["💬 Live Simulator", "⚙️ My Settings"])

    # --- TAB 1: SIMULATOR ---
    with tab_sim:
        # Initialize Chat
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": f"Hi! I'm the AI for {client_name}. I've loaded your products."}]

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Test your bot..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("AI is checking your feed..."):
                try:
                    # FETCH LIVE DATA (Using the SAVED URL)
                    if saved_feed:
                        try:
                            df = pd.read_csv(saved_feed)
                            catalog_str = df.to_string(index=False)
                        except:
                            catalog_str = "Error reading feed."
                    else:
                        catalog_str = "No feed connected."

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
                                st.balloons()
                                st.success(f"✅ NEW ORDER: {ai_action.get('item')}")
                                st.session_state.orders.append(ai_action)
                                # Trigger Webhook (Using the SAVED URL)
                                if saved_webhook:
                                    requests.post(saved_webhook, json=ai_action)
                            
                            with st.chat_message("assistant"):
                                st.markdown(msg_text)
                            st.session_state.messages.append({"role": "assistant", "content": msg_text})
                        except:
                            st.error("Bot is thinking...")
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- TAB 2: SETTINGS (READ ONLY FOR CLIENT) ---
    with tab_settings:
        st.info("ℹ️ These settings are managed by your Account Manager. Contact support to update.")
        st.text_input("Live Feed URL", value=saved_feed, disabled=True)
        st.text_input("Webhook URL", value=saved_webhook, disabled=True)
        st.text_area("Store Policy", value=saved_policy, disabled=True)
        
        # WIDGET CODE GENERATOR
        st.subheader("🔌 Your Website Code")
        code = f"""<script>window.BOT_CONFIG={{workerUrl:"{WORKER_URL}",policy:"{saved_policy[:50]}..."}}</script>
<script src="https://cdn.jsdelivr.net/gh/farhanmc011/chat-widget@main/widget.js" async></script>"""
        st.code(code, language="html")
