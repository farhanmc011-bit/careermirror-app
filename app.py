import streamlit as st
import requests

# --- CONFIGURATION ---
# This is your actual Make.com URL
WEBHOOK_URL = "https://hook.us2.make.com/8x73b7bfbqzjey5zkvp8gs0j28d78pwd"

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
                # Send data to Make.com -> Cloudflare AI
                payload = {"resume": resume, "jobDescription": job}
                response = requests.post(WEBHOOK_URL, json=payload)
                
                # Display Result
                if response.status_code == 200:
                    st.success("Success! Here is your optimized resume:")
                    st.markdown("---")
                    st.markdown(response.text) # Displays the AI output
                else:
                    st.error("Error connecting to the server.")
            except Exception as e:
                st.error(f"Something went wrong: {e}")
