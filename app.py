import streamlit as st
import requests
import json

# --- CONFIGURATION ---
WORKER_URL = "https://llm-chat-app-template.farhanmc011.workers.dev" # Your Brain

st.set_page_config(page_title="ShopSales Admin", page_icon="⚙️", layout="wide")

st.title("⚙️ ShopSales: Admin Dashboard")
st.caption("Configure your bot and put it on your store.")

# --- TABS ---
tab1, tab2 = st.tabs(["1. Train Your Bot", "2. Get Widget Code"])

with tab1:
    st.header("🧠 Knowledge Base")
    st.write("Teach your bot about your store.")
    
    products = st.text_area("Product Catalog", height=150, value="Red T-Shirt ($20)\nBlue Jeans ($50)")
    policy = st.text_area("Store Policy", height=100, value="Shipping is free over $100. Returns 30 days.")
    
    if st.button("Save Training Data"):
        # In a real SaaS, this would save to a database. 
        # For MVP, we just show success.
        st.success("Brain Updated! Now go to Tab 2.")

with tab2:
    st.header("🔌 Connect to Your Store")
    st.write("Copy this code and paste it into your Shopify/Wix/WordPress 'Header' or 'Footer' section.")
    
    # THE MAGIC SCRIPT
    # This script creates a chat bubble that talks to YOUR Cloudflare Worker
    widget_code = f"""
<script>
  window.BOT_CONFIG = {{
    workerUrl: "{WORKER_URL}",
    policy: `{policy}`, 
    products: `{products}`
  }};
</script>
<script src="https://cdn.jsdelivr.net/gh/farhanmc011/chat-widget@main/widget.js" async></script>
    """
    
    st.code(widget_code, language="html")
    
    st.info("💡 Once you paste this, the 'ShopSales' bubble will appear on your site instantly.")
