import streamlit as st
import requests
import pandas as pd
import json
import re
import time
from datetime import datetime

# --- ⚙️ CONFIGURATION ---
# PASTE YOUR CLOUDFLARE WORKER URL HERE
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" 

# --- 🎨 PAGE CONFIG & CSS ---
st.set_page_config(page_title="Omni-Agent v3", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* MAIN THEME */
    .stApp {
        background-color: #050505;
        color: #ffffff;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #1f1f1f;
    }
    
    /* METRIC CARDS */
    .metric-card {
        background: linear-gradient(145deg, #111111, #0a0a0a);
        border: 1px solid #222;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-card h3 { color: #666; font-size: 12px; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px;}
    .metric-card h2 { color: #fff; font-size: 28px; font-weight: 700; margin: 0; }
    .metric-card span { font-size: 14px; font-weight: bold; }
    
    /* NEON TEXT */
    .neon-green { color: #00FF94 !important; }
    .neon-blue { color: #00E5FF !important; }
    .neon-purple { color: #BD00FF !important; }

    /* BUTTONS */
    .stButton>button {
        background-color: #1f1f1f;
        color: white;
        border: 1px solid #333;
        border-radius: 6px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #00FF94;
        color: #00FF94;
    }
    
    /* HIDE STREAMLIT UI */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 📦 SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_config" not in st.session_state: st.session_state.user_config = {}
if "orders" not in st.session_state: st.session_state.orders = []
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "System Ready. Waiting for customer input."}]

# ==========================================
# 🔐 1. LOGIN SYSTEM (The Gate)
# ==========================================
def login_page():
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; font-size: 50px;'>⚡</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>OMNI-AGENT v3.0</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Enterprise AI Operating System</p>", unsafe_allow_html=True)
        
        with st.form("login"):
            username = st.text_input("Client ID", placeholder="e.g. demo")
            password = st.text_input("Access Key", type="password", placeholder="••••••")
            
            if st.form_submit_button("AUTHENTICATE"):
                try:
                    user = st.secrets["users"].get(username)
                    if user and user["password"] == password:
                        st.session_state.logged_in = True
                        st.session_state.user_config = user
                        st.rerun()
                    else:
                        st.error("⛔ ACCESS DENIED")
                except:
                    st.error("⚠️ SYSTEM ERROR: Database not found.")

# ==========================================
# 🖥️ 2. MAIN APPLICATION (The Views)
# ==========================================
def main_app():
    # --- SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.markdown("## ⚡ OMNI v3")
        st.caption(f"Logged in as: {st.session_state.user_config.get('name')}")
        st.markdown("---")
        
        menu = st.radio("MENU", ["📊 Dashboard", "💬 Live Inbox", "📦 Order Manager", "🔌 Integration"], label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # --- VIEW 1: DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("📊 Executive Overview")
        st.markdown("Real-time performance metrics.")
        
        # KEY METRICS
        total_rev = sum([o.get('quantity', 1) * 20 for o in st.session_state.orders])
        total_orders = len(st.session_state.orders)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"""<div class="metric-card"><h3>Revenue</h3><h2 class="neon-green">${total_rev}</h2></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="metric-card"><h3>Total Orders</h3><h2 class="neon-blue">{total_orders}</h2></div>""", unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class="metric-card"><h3>Conversion</h3><h2 class="neon-purple">{min(total_orders * 10, 100)}%</h2></div>""", unsafe_allow_html=True)
        with c4: st.markdown(f"""<div class="metric-card"><h3>System Status</h3><h2 style="color:#00FF94;">ONLINE</h2></div>""", unsafe_allow_html=True)

        st.markdown("###")
        
        # CHART (Visuals make it look expensive)
        st.subheader("📈 Sales Velocity")
        if total_orders > 0:
            chart_data = pd.DataFrame({
                "Order": [f"Order #{i+1}" for i in range(total_orders)],
                "Value": [20] * total_orders
            })
            st.bar_chart(chart_data, x="Order", y="Value", color="#00FF94")
        else:
            st.info("Waiting for first sale to generate analytics...")

    # --- VIEW 2: LIVE INBOX (The Simulator) ---
    elif menu == "💬 Live Inbox":
        st.title("💬 Live Customer Simulator")
        st.caption("Test your AI Agent's responses in real-time.")
        
        # Chat Container
        chat_container = st.container(height=500)
        
        # Render History
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        # Input
        if prompt := st.chat_input("Type a message as a customer..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"): st.write(prompt)
                
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("⚡ *AI is processing...*")
                    
                    try:
                        # GET CONFIG
                        config = st.session_state.user_config
                        
                        # FETCH FEED (If available)
                        catalog_str = "No Feed."
                        if config.get("feed_url"):
                            try:
                                df = pd.read_csv(config.get("feed_url"))
                                catalog_str = df.to_string(index=False)
                            except: pass
                        
                        # CALL WORKER
                        payload = {
                            "store_policy": config.get("policy", "Standard"),
                            "product_catalog": catalog_str,
                            "user_question": prompt
                        }
                        response = requests.post(WORKER_URL, json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            raw_text = data.get("result", {}).get("response", "") or data.get("response", "") or str(data)
                            
                            # SMART PARSE
                            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                            if json_match:
                                clean_json = json_match.group(0)
                                try:
                                    ai_action = json.loads(clean_json)
                                    final_msg = ai_action.get("message", "...")
                                    
                                    # HANDLE ORDER
                                    if ai_action.get("action") == "CREATE_ORDER":
                                        st.toast(f"🚀 ORDER RECEIVED: {ai_action.get('item')}", icon="✅")
                                        # Add Timestamp
                                        ai_action["time"] = datetime.now().strftime("%H:%M:%S")
                                        st.session_state.orders.append(ai_action)
                                        
                                        # Webhook Trigger
                                        if config.get("webhook_url"):
                                            requests.post(config.get("webhook_url"), json=ai_action)
                                    
                                    message_placeholder.write(final_msg)
                                    st.session_state.messages.append({"role": "assistant", "content": final_msg})
                                except:
                                    message_placeholder.error("JSON Parsing Error")
                            else:
                                message_placeholder.write(raw_text) # Fallback if no JSON
                        else:
                            message_placeholder.error("Server Error")
                    except Exception as e:
                        message_placeholder.error(f"Connection Failed: {e}")

    # --- VIEW 3: ORDER MANAGER ---
    elif menu == "📦 Order Manager":
        st.title("📦 Order Management")
        st.markdown("All orders generated by the AI.")
        
        if st.session_state.orders:
            # Convert JSON list to DataFrame for a nice table
            df_orders = pd.DataFrame(st.session_state.orders)
            # Reorder columns if possible
            cols = ["time", "item", "quantity", "action"]
            available_cols = [c for c in cols if c in df_orders.columns]
            st.dataframe(df_orders[available_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No orders received yet.")

    # --- VIEW 4: INTEGRATION ---
    elif menu == "🔌 Integration":
        st.title("🔌 Integration Hub")
        st.markdown("Connect your AI to the world.")
        
        t1, t2 = st.tabs(["Website Widget", "Data Source"])
        
        with t1:
            st.subheader("Website Installation")
            st.code(f"""<script>
  window.BOT_CONFIG = {{
    workerUrl: "{WORKER_URL}",
    policy: "{st.session_state.user_config.get('policy', '')}"
  }};
</script>
<script src="https://cdn.jsdelivr.net/gh/farhanmc011/chat-widget@main/widget.js" async></script>""", language="html")
            st.caption("Copy and paste this into your HTML/Shopify Theme.")

        with t2:
            st.subheader("Live Data")
            st.text_input("Current Feed URL", value=st.session_state.user_config.get("feed_url", ""), disabled=True)
            st.caption("To update this, contact your Account Manager.")

# --- 🚀 RUN APP ---
if st.session_state.logged_in:
    main_app()
else:
    login_page()
