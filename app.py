import streamlit as st
import requests
import json

# --- CONFIGURATION ---
# 🔴 PASTE YOUR NEW WORKER URL HERE 🔴
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" 

# --- PAGE CONFIG ---
st.set_page_config(page_title="ShopSales Admin", page_icon="🛍️", layout="wide")

st.markdown("""
<style>
    .order-box { 
        padding: 1rem; 
        background-color: #e3fcf7; 
        border: 1px solid #008060; 
        border-radius: 8px; 
        margin-bottom: 10px; 
    }
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        font-weight: bold; 
        background-color: #008060; 
        color: white; 
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("🛍️ ShopSales: Admin Dashboard")
st.caption("Configure your AI Agent & Get the Widget Code.")

# --- TABS ---
tab1, tab2 = st.tabs(["1. Test Simulator", "2. Get Widget Code"])

# --- TAB 1: SIMULATOR (TESTING) ---
with tab1:
    col_setup, col_chat = st.columns([1, 2])
    
    with col_setup:
        st.header("📦 Inventory & Rules")
        products = st.text_area("Product Catalog", height=150, value="Red T-Shirt ($20)\nBlue Jeans ($50)\nWhite Sneakers ($80)")
        policy = st.text_area("Store Policy", height=100, value="Shipping is free over $100. Returns 30 days.")
        st.info("Edit these to change how the bot behaves!")

    with col_chat:
        st.subheader("💬 Live Chat Preview")

        # Session State
        if "orders" not in st.session_state:
            st.session_state.orders = []
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Hi! I can help with support OR take your order. Try saying 'I want the Red Shirt'."}]

        # Display Chat
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Display Orders
        if st.session_state.orders:
            st.markdown("### 🛒 Active Orders (Automated)")
            for order in st.session_state.orders:
                st.markdown(f"""
                <div class="order-box">
                    <b>✅ Order Created Automatically</b><br>
                    Item: {order['item']} | Qty: {order['quantity']} | Status: <b>Processing</b>
                </div>
                """, unsafe_allow_html=True)

        # Input
        if prompt := st.chat_input("Customer says..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("AI is thinking..."):
                try:
                    payload = {
                        "store_policy": policy, 
                        "product_catalog": products,
                        "user_question": prompt
                    }
                    
                    response = requests.post(WORKER_URL, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Clean JSON
                        raw_json = data.get("result", {}).get("response", "") or data.get("response", "")
                        clean_json = raw_json.replace("```json", "").replace("```", "").strip()
                        
                        try:
                            ai_action = json.loads(clean_json)
                            message_text = ai_action.get("message", "Processed.")
                            
                            if ai_action.get("action") == "CREATE_ORDER":
                                new_order = {"item": ai_action.get("item"), "quantity": ai_action.get("quantity")}
                                st.session_state.orders.append(new_order)
                                st.balloons() 
                            
                            with st.chat_message("assistant"):
                                st.markdown(message_text)
                            st.session_state.messages.append({"role": "assistant", "content": message_text})
                            
                        except Exception as e:
                            st.error(f"Bot Parsing Error: {clean_json}")
                    else:
                        st.error("Server Error")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# --- TAB 2: WIDGET CODE (SELLING) ---
with tab2:
    st.header("🔌 Install on Website")
    st.write("Copy this code and give it to your client (or paste in Shopify).")
    
    widget_code = f"""
<script>
  window.BOT_CONFIG = {{
    workerUrl: "{WORKER_URL}",
    policy: "Shipping is free over $100...", 
    products: "Red T-Shirt ($20)..."
  }};
</script>
<script src="https://cdn.jsdelivr.net/gh/farhanmc011/chat-widget@main/widget.js" async></script>
    """
    st.code(widget_code, language="html")
