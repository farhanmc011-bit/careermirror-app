import streamlit as st
import requests
import pandas as pd
import json

# --- CONFIGURATION ---
# 🔴 PASTE YOUR WORKER URL HERE (The one ending in .workers.dev)
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" 

# --- PAGE CONFIG ---
st.set_page_config(page_title="Omni-Agent Admin", page_icon="🛍️", layout="wide")

st.title("🛍️ Omni-Agent: Auto-Pilot Mode")
st.caption("Live Store Sync & Automated Fulfillment.")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["1. Auto-Sync (Live Feed)", "2. Test Simulator", "3. Order Fulfillment"])

# --- SESSION STATE ---
if "catalog_data" not in st.session_state:
    st.session_state.catalog_data = "No products loaded yet."
if "orders" not in st.session_state:
    st.session_state.orders = []

# --- TAB 1: THE LAZY SYNC ---
with tab1:
    st.header("🔄 Live Store Sync")
    st.info("💡 Strategy: Ask the client for their 'Facebook/Google Shopping Feed URL'. Every Shopify store has one.")
    
    # Pre-filled with a dummy CSV for testing
    feed_url = st.text_input("Paste Live Product Feed URL (CSV)", value="https://raw.githubusercontent.com/farhanmc011/chat-widget/main/demo_products.csv")
    
    if st.button("🔗 Connect Live Feed"):
        if feed_url:
            with st.spinner("Fetching live data from store..."):
                try:
                    # Read the CSV Feed
                    df = pd.read_csv(feed_url)
                    # Convert to string for the AI Brain
                    st.session_state.catalog_data = df.to_string(index=False)
                    st.success("✅ Connected! The AI will now check this link before every answer.")
                    st.dataframe(df) # Show the client their data
                except Exception as e:
                    st.error(f"Could not read feed. Ensure it's a direct CSV link. Error: {e}")
        else:
            st.warning("Paste the link first.")

    st.subheader("Store Rules")
    policy = st.text_area("Store Policy", height=100, value="Shipping is free over $100. Returns 30 days.")

# --- TAB 2: SIMULATOR ---
with tab2:
    st.subheader("💬 Test the Brain")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! I'm synced with your live store."}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about a product..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("AI is checking live feed..."):
            try:
                payload = {
                    "store_policy": policy, 
                    "product_catalog": st.session_state.catalog_data,
                    "user_question": prompt
                }
                
                response = requests.post(WORKER_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    # Clean JSON output from Llama
                    raw_json = data.get("result", {}).get("response", "") or data.get("response", "")
                    clean_json = raw_json.replace("```json", "").replace("```", "").strip()
                    
                    try:
                        ai_action = json.loads(clean_json)
                        message_text = ai_action.get("message", "Processed.")
                        
                        # IF AI SELLS SOMETHING:
                        if ai_action.get("action") == "CREATE_ORDER":
                            st.balloons()
                            st.success(f"✅ AI generated ORDER SIGNAL for: {ai_action.get('item')}")
                            st.info("ℹ️ Sending this signal to Tab 3 (Make.com)...")
                            # Save to session for demo
                            st.session_state.orders.append(ai_action)
                        
                        with st.chat_message("assistant"):
                            st.markdown(message_text)
                        st.session_state.messages.append({"role": "assistant", "content": message_text})
                    except:
                        st.error(f"Parsing Error: {clean_json}")
                else:
                    st.error("Server Error")
            except Exception as e:
                st.error(f"Error: {e}")

# --- TAB 3: THE REAL ORDER SETUP ---
with tab3:
    st.header("🚚 Order Fulfillment (Make.com)")
    st.write("This is where we turn the 'Signal' into a 'Shipment'.")
    
    st.markdown("### The Workflow:")
    st.info("User Buys -> AI Creates JSON -> Sends to Webhook -> Make.com -> **Create Shopify Order**")

    webhook_url = st.text_input("Make.com Webhook URL", placeholder="https://hook.us1.make.com/...")
    
    st.markdown("### Test Connection")
    if st.button("🔴 Send Test Order to Warehouse"):
        if webhook_url:
            try:
                # Send a dummy order to test the connection
                test_order = {"action": "TEST", "item": "Test Product", "price": 0, "customer": "Test User"}
                requests.post(webhook_url, json=test_order)
                st.success("✅ Signal Sent! Check your Make.com history.")
            except:
                st.error("Connection Failed.")
        else:
            st.warning("Enter a Webhook URL first.")
            
    # Show automated orders log
    if st.session_state.orders:
        st.write("Recent AI Orders:")
        st.json(st.session_state.orders)
