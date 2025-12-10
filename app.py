import streamlit as st
import requests
import json

# --- CONFIGURATION ---
# PASTE YOUR CLOUDFLARE WORKER URL BELOW
WORKER_URL = "https://careermirror-brain.farhanmc011.workers.dev" 

# --- PAGE SETUP ---
st.set_page_config(page_title="CareerMirror AI", page_icon="👔")
st.title("CareerMirror AI 👔")
st.markdown("### Bypass the ATS. Get the Interview.")
st.write("Paste your resume and the job description below. AI will rewrite your resume to match the job keywords.")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    resume = st.text_area("Paste Your Resume", height=300)
with col2:
    job = st.text_area("Paste Job Description", height=300)

# --- THE BUTTON ---
if st.button("Optimize My Resume", type="primary"):
    if not resume or not job:
        st.error("Please fill in both text boxes!")
    else:
        with st.spinner("AI is analyzing keywords..."):
            try:
                # Direct connection to Cloudflare
                payload = {"resume": resume, "jobDescription": job}
                response = requests.post(WORKER_URL, json=payload)
                
                # Check if successful
                if response.status_code == 200:
                    # Parse the JSON response
                    result_json = response.json()
                    
                    # Extract just the text from the "response" or "result" field
                    if "response" in result_json:
                        final_text = result_json["response"]
                    elif "result" in result_json:
                         final_text = result_json["result"]["response"]
                    else:
                        final_text = str(result_json)
                    
                    st.success("Success! Here is your optimized resume:")
                    st.markdown("---")
                    st.markdown(final_text) 
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")
