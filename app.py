import streamlit as st
import requests
import pandas as pd
import json

# --- CONFIGURATION ---
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" 

# --- PAGE CONFIG ---
st.set_page_config(page_title="Omni-Agent", page_icon="🛍️", layout="wide")

# --- CSS FOR CLEAN LOOK ---
st.markdown("""
<style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00cc66;
        text-align: center;
    }
    .status-badge {
        background-color: #d1fae5;
        color: #065f46;
        padding: 5px 10px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 12px;
    }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "catalog_data" not in st.session_state:
    st.session_state.catalog_data = "No products loaded."
if "orders" not in st.session_state:
    st.session_state.orders = []
if "feed_url" not in st.session_state:
    st.session_state.feed_url = ""
if "webhook_url" not in st.session_state:
    st.session_state.webhook_url = ""

# --- SIDEBAR (THE MODE SWITCH) ---
with st.sidebar:
    st.title("🛍️ Omni-Agent")
    st.write("v1.0.0")
    st.markdown("---")
    
    # THE SECRET SWITCH
    # In a real app, you would hide this behind a password.
    mode = st.radio("Display Mode", ["Client Dashboard", "Admin Setup 🔧"])
    
    st.markdown("---")
    if mode == "Client Dashboard":
        st.success("🟢 System Online")
        st.write("Bot Status: **Active**")
        st.write("Live Feed: **Connected**")

# ==========================================
# 1. CLIENT DASHBOARD (CLEAN VIEW)
# ==========================================
if mode == "Client Dashboard":
    st.title("👋 Welcome back, Store Owner")
    
    # METRICS ROW
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="metric-box">
            <h3>💰 Total Sales</h3>
            <h2>${sum([o.get('quantity', 1) * 20 for o in st.session_state.orders])}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-box">
            <h3>📦 Orders Generated</h3>
            <h2>{len(st.session_state.orders)}</h2>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-box">
            <h3>⚡ Response Time</h3>
            <h2>0.8s</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("###")
    
    # LIVE CHAT PREVIEW (Clean, no JSON)
    st.subheader("💬 Live Bot Preview")
    st.caption("This is exactly what your customers see.")

    # Initialize Chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm your store assistant. Ask me anything!"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Test your bot..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Bot is typing..."):
            try:
                # Use the saved settings
                payload = {
                    "store_policy": "Standard Shipping.", 
                    "product_catalog": st.session_state.catalog_data,
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
                            # Clean "Order Card" for Client
                            st.success(f"✅ NEW ORDER RECEIVED: {ai_action.get('item')}")
                            st.session_state.orders.append(ai_action)
                            
                            # Fire Webhook silently (if set)
                            if st.session_state.webhook_url:
                                requests.post(st.session_state.webhook_url, json=ai_action)
                        
                        with st.chat_message("assistant"):
                            st.markdown(msg_text)
                        st.session_state.messages.append({"role": "assistant", "content": msg_text})
                    except:
                        st.error("Bot is updating...")
            except:
                st.error("Connection issue.")

# ==========================================
# 2. ADMIN SETUP (TECHNICAL VIEW)
# ==========================================
else:
    st.header("🔧 Admin Configuration")
    st.warning("⚠️ Restricted Area: Technical Setup Only")
    
    tab1, tab2 = st.tabs(["1. Connect Data", "2. Connect Fulfillment"])
    
    with tab1:
        st.subheader("Data Sources")
        new_feed = st.text_input("Product Feed URL (CSV)", value=st.session_state.feed_url)
        if st.button("Save & Sync Feed"):
            st.session_state.feed_url = new_feed
            try:
                df = pd.read_csv(new_feed)
                st.session_state.catalog_data = df.to_string(index=False)
                st.success("✅ Feed Synced Successfully!")
            except:
                st.error("Invalid URL")
                
    with tab2:
        st.subheader("Make.com Integration")
        new_hook = st.text_input("Webhook URL", value=st.session_state.webhook_url)
        if st.button("Save Webhook"):
            st.session_state.webhook_url = new_hook
            st.success("✅ Fulfillment Connected!")
