import streamlit as st
import requests
import json

# --- CONFIGURATION ---
# Your New Brain URL (I pasted it here for you)
WORKER_URL = "https://llm-chat-app-template.farhanmc011.workers.dev"

# --- PAGE CONFIG ---
st.set_page_config(page_title="ShopSales AI", page_icon="🛍️", layout="wide")

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
st.title("🛍️ ShopSales AI")
st.caption("The AI Agent that Support AND Sells.")

# --- SIDEBAR (STORE DATABASE) ---
with st.sidebar:
    st.header("📦 Live Inventory")
    # Simulate a product database - You can edit this later!
    products = st.text_area("Product Catalog", height=150, value="Red T-Shirt ($20)\nBlue Jeans ($50)\nWhite Sneakers ($80)")
    
    st.header("⚙️ Store Rules")
    policy = st.text_area("Store Policy", height=100, value="Shipping is free over $100. Returns 30 days.")

# --- CHAT INTERFACE ---
st.subheader("💬 Customer Chat Simulator")

# Session State for Orders & Messages
if "orders" not in st.session_state:
    st.session_state.orders = []
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I can help with support OR take your order. Try saying 'I want the Red Shirt'."}]

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Display Created Orders (The Automation)
if st.session_state.orders:
    st.markdown("### 🛒 Active Orders (Automated)")
    for order in st.session_state.orders:
        st.markdown(f"""
        <div class="order-box">
            <b>✅ Order Created Automatically</b><br>
            Item: {order['item']} | Qty: {order['quantity']} | Status: <b>Processing</b>
        </div>
        """, unsafe_allow_html=True)

# User Input
if prompt := st.chat_input("Customer says..."):
    # 1. Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Get AI Response
    with st.spinner("AI is checking inventory..."):
        try:
            payload = {
                "store_policy": policy, 
                "product_catalog": products,
                "user_question": prompt
            }
            
            response = requests.post(WORKER_URL, json=payload)
            
            if response.status_code == 200:
                # Parse the JSON response from Cloudflare
                data = response.json()
                
                # Logic to clean up Llama output (it sometimes adds markdown wrappers)
                raw_json = data.get("result", {}).get("response", "") or data.get("response", "")
                clean_json = raw_json.replace("```json", "").replace("```", "").strip()
                
                try:
                    # Convert text to JSON object
                    ai_action = json.loads(clean_json)
                    
                    # Extract the message to show the user
                    message_text = ai_action.get("message", "Processed.")
                    
                    # CHECK: Did the AI make a sale?
                    if ai_action.get("action") == "CREATE_ORDER":
                        # AUTOMATION TRIGGERS HERE
                        new_order = {"item": ai_action.get("item"), "quantity": ai_action.get("quantity")}
                        st.session_state.orders.append(new_order)
                        st.balloons() # Visual celebration!
                    
                    # Display Bot Message
                    with st.chat_message("assistant"):
                        st.markdown(message_text)
                    st.session_state.messages.append({"role": "assistant", "content": message_text})
                    
                except Exception as e:
                    st.error(f"Bot Parsing Error: {clean_json}")
            else:
                st.error("Server Error: Check your URL")
        except Exception as e:
            st.error(f"Connection Error: {e}")
