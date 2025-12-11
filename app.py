import streamlit as st
import requests
import pandas as pd
import json
import re
import time
from datetime import datetime

# --- ⚙️ CONFIGURATION ---
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" 

# --- 🎨 PAGE CONFIG & LUXURY WHITE CSS ---
st.set_page_config(page_title="Client Portal", page_icon="✨", layout="wide")

st.markdown("""
<style>
    /* 1. MAIN THEME - LUXURY WHITE */
    .stApp {
        background-color: #F8F9FB; /* Very soft blue-grey */
        color: #1A1A1A; /* Near Black */
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* 2. SIDEBAR - CLEAN WHITE */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB; /* Subtle divider */
    }
    
    /* 3. METRIC CARDS - APPLE STYLE */
    .metric-card {
        background: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #F0F0F0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); /* Soft, expensive shadow */
        text-align: left; /* Professional alignment */
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.06);
    }
    .metric-card h3 { 
        color: #6B7280; /* Cool Grey */
        font-size: 13px; 
        text-transform: uppercase; 
        font-weight: 600; 
        letter-spacing: 0.5px;
        margin-bottom: 8px; 
    }
    .metric-card h2 { 
        color: #111827; /* Deep Black */
        font-size: 32px; 
        font-weight: 700; 
        margin: 0; 
    }
    
    /* 4. BUTTONS - MINIMALIST BLACK */
    .stButton>button {
        background-color: #000000;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: white;
        transform: scale(1.02);
    }

    /* 5. INPUT FIELDS - CLEAN */
    .stTextInput>div>div>input {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        color: #1A1A1A;
    }

    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 📦 SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_config" not in st.session_state: st.session_state.user_config = {}
if "orders" not in st.session_state: st.session_state.orders = []
if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Welcome. I am ready to assist your customers."}]

# ==========================================
# 🔐 1. LOGIN SYSTEM (Minimalist)
# ==========================================
def login_page():
    c1, c2, c3 = st.columns([1, 0.8, 1])
    with c2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # Clean Logo Area
        st.markdown("<h2 style='text-align: center; color: #111827; margin-bottom: 0px;'>Client Portal</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6B7280; font-size: 14px;'>Secure Access • Enterprise Edition</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            # Full Width Button Hack
            submitted = st.form_submit_button("Sign In →")
            
            if submitted:
                try:
                    user = st.secrets["users"].get(username)
                    if user and user["password"] == password:
                        st.session_state.logged_in = True
                        st.session_state.user_config = user
                        st.rerun()
                    else:
                        st.error("Incorrect credentials.")
                except:
                    st.error("System configuration error.")

# ==========================================
# 🖥️ 2. MAIN APPLICATION (The Pro View)
# ==========================================
def main_app():
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("### 🏢 Portal")
        st.caption(f"Account: {st.session_state.user_config.get('name')}")
        st.markdown("---")
        
        # Navigation
        menu = st.radio("Navigate", ["Overview", "Live Chat", "Orders", "Settings"], label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.rerun()

    # --- VIEW 1: OVERVIEW (Dashboard) ---
    if menu == "Overview":
        st.title("Performance Overview")
        st.markdown("Real-time sales and interaction metrics.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Metrics
        total_rev = sum([o.get('quantity', 1) * 20 for o in st.session_state.orders])
        total_orders = len(st.session_state.orders)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"""<div class="metric-card"><h3>Total Revenue</h3><h2>${total_rev}</h2></div>""", unsafe_allow_html=True)
        with c2: st.markdown(f"""<div class="metric-card"><h3>Orders Processed</h3><h2>{total_orders}</h2></div>""", unsafe_allow_html=True)
        with c3: st.markdown(f"""<div class="metric-card"><h3>Active Products</h3><h2>Synced</h2></div>""", unsafe_allow_html=True)
        with c4: st.markdown(f"""<div class="metric-card"><h3>System Health</h3><h2 style="color:#10B981;">100%</h2></div>""", unsafe_allow_html=True)

        st.markdown("###")
        st.subheader("Sales Activity")
        if total_orders > 0:
            chart_data = pd.DataFrame({"Order": [f"#{i+1}" for i in range(total_orders)], "Revenue": [20] * total_orders})
            st.bar_chart(chart_data, x="Order", y="Revenue", color="#111827") # Black bars
        else:
            st.info("No data available. Waiting for first interaction.")

    # --- VIEW 2: LIVE CHAT (Clean Inbox) ---
    elif menu == "Live Chat":
        st.title("Live Interaction Simulator")
        st.caption("Preview how your AI Assistant interacts with customers.")
        
        # Clean Chat UI
        for msg in st.session_state.messages:
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

        if prompt := st.chat_input("Type a message..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar="👤"): st.write(prompt)
            
            with st.chat_message("assistant", avatar="🤖"):
                placeholder = st.empty()
                placeholder.markdown("Thinking...")
                
                try:
                    # Logic
                    config = st.session_state.user_config
                    catalog_str = "No Feed."
                    if config.get("feed_url"):
                        try:
                            df = pd.read_csv(config.get("feed_url"))
                            catalog_str = df.to_string(index=False)
                        except: pass
                    
                    payload = {"store_policy": config.get("policy", "Standard"), "product_catalog": catalog_str, "user_question": prompt}
                    response = requests.post(WORKER_URL, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        raw_text = data.get("result", {}).get("response", "") or data.get("response", "") or str(data)
                        
                        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                        if json_match:
                            ai_action = json.loads(json_match.group(0))
                            msg_text = ai_action.get("message", "...")
                            
                            if ai_action.get("action") == "CREATE_ORDER":
                                st.success(f"Order Confirmed: {ai_action.get('item')}")
                                ai_action["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                st.session_state.orders.append(ai_action)
                                if config.get("webhook_url"): requests.post(config.get("webhook_url"), json=ai_action)
                            
                            placeholder.write(msg_text)
                            st.session_state.messages.append({"role": "assistant", "content": msg_text})
                        else:
                            placeholder.write(raw_text)
                    else:
                        placeholder.error("Connection Error")
                except Exception as e:
                    placeholder.error(f"Error: {e}")

    # --- VIEW 3: ORDERS (Table View) ---
    elif menu == "Orders":
        st.title("Order History")
        
        if st.session_state.orders:
            df = pd.DataFrame(st.session_state.orders)
            # Clean Table
            st.dataframe(
                df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "item": "Product Name",
                    "quantity": "Qty",
                    "date": "Date & Time",
                    "message": None, # Hide internal message
                    "action": None   # Hide internal action code
                }
            )
        else:
            st.info("No orders found in this session.")

    # --- VIEW 4: SETTINGS (Integration) ---
    elif menu == "Settings":
        st.title("System Configuration")
        
        st.subheader("Website Widget Code")
        st.markdown("Copy and paste this code into your website's `<body>` tag.")
        st.code(f"""<script>
window.BOT_CONFIG = {{
  workerUrl: "{WORKER_URL}",
  policy: "{st.session_state.user_config.get('policy', 'Standard')}"
}};
</script>
<script src="https://cdn.jsdelivr.net/gh/farhanmc011/chat-widget@main/widget.js" async></script>""", language="html")

        st.markdown("---")
        st.subheader("Data Connections")
        st.text_input("Active Product Feed", value=st.session_state.user_config.get("feed_url", "Not Connected"), disabled=True)
        st.caption("Managed by Administrator")

# --- 🚀 RUN ---
if st.session_state.logged_in:
    main_app()
else:
    login_page()
