import streamlit as st
import requests
import pandas as pd
import io

# --- CONFIGURATION ---
WORKER_URL = "https://shop-brain.farhanmc011.workers.dev" # Your Brain URL

st.set_page_config(page_title="Omni-Agent Admin", page_icon="🌐", layout="wide")

st.title("🌐 Omni-Agent: Central Command")
st.caption("Sync Google Sheets & Connect to WhatsApp/Insta.")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["1. Auto-Catalog (Google Sheets)", "2. Test Simulator", "3. Connect Channels"])

# --- SESSION STATE ---
if "catalog_data" not in st.session_state:
    st.session_state.catalog_data = "No products loaded yet."

# --- TAB 1: GOOGLE SHEETS AUTOMATION ---
with tab1:
    st.header("📊 Live Inventory Sync")
    st.write("Don't type manually. Just paste your Google Sheet 'Published CSV' link.")
    
    sheet_url = st.text_input("Paste Google Sheet CSV Link", placeholder="https://docs.google.com/spreadsheets/d/.../export?format=csv")
    
    if st.button("🔄 Sync Catalog Now"):
        if sheet_url:
            try:
                # Automate the fetching
                df = pd.read_csv(sheet_url)
                # Convert to text string for the AI
                st.session_state.catalog_data = df.to_string(index=False)
                st.success("✅ Catalog Synced! The Bot now knows your live inventory.")
                st.dataframe(df) # Show the client their data
            except Exception as e:
                st.error(f"Error reading sheet. Make sure it is public! {e}")
        else:
            st.warning("Paste a link first.")

    st.subheader("Store Rules")
    policy = st.text_area("Store Policy", height=100, value="Shipping is free over $100. Returns 30 days.")

# --- TAB 2: SIMULATOR ---
with tab2:
    st.subheader("💬 Test with Live Data")
    
    # Initialize chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi! Check my live inventory from Google Sheets."}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about products in the sheet..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Checking Google Sheet..."):
            try:
                # SEND LIVE SHEET DATA TO BRAIN
                payload = {
                    "store_policy": policy, 
                    "product_catalog": st.session_state.catalog_data, # This comes from the Sheet!
                    "user_question": prompt
                }
                
                response = requests.post(WORKER_URL, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    # Clean & Parse
                    raw_json = data.get("result", {}).get("response", "") or data.get("response", "")
                    clean_json = raw_json.replace("```json", "").replace("```", "").strip()
                    
                    try:
                        import json
                        ai_action = json.loads(clean_json)
                        message_text = ai_action.get("message", "Processed.")
                        
                        if ai_action.get("action") == "CREATE_ORDER":
                            st.balloons()
                            st.success(f"✅ Order for {ai_action.get('item')} confirmed!")
                        
                        with st.chat_message("assistant"):
                            st.markdown(message_text)
                        st.session_state.messages.append({"role": "assistant", "content": message_text})
                    except:
                        st.error("Parsing Error")
                else:
                    st.error("Server Error")
            except Exception as e:
                st.error(f"Error: {e}")

# --- TAB 3: OMNICHANNEL (THE BILLIONAIRE MOVE) ---
with tab3:
    st.header("🔗 Connect Messaging Apps")
    st.info("To connect WhatsApp & Instagram, we use the API Endpoint below.")
    
    st.markdown("### Your Universal API Endpoint")
    st.code(WORKER_URL, language="text")
    
    st.markdown("### How to Connect (The Strategy):")
    st.write("1. Go to **Make.com** (Free).")
    st.write("2. Create a Scenario: **WhatsApp Watch Messages** -> **HTTP Request (Your API)**.")
    st.write("3. The Bot will now reply on WhatsApp automatically using the same Brain.")
