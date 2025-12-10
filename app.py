import streamlit as st
import requests
from fpdf import FPDF

# --- CONFIGURATION ---
WORKER_URL = "https://careermirror-engine1.farhanmc011.workers.dev"

# --- PAGE CONFIG ---
st.set_page_config(page_title="CareerMirror AI", page_icon="TK", layout="centered")

# Custom CSS for the "Pro" look
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("CareerMirror AI 👔")
st.caption("🚀 The 'Zero-to-One' Resume Optimizer")
st.markdown("---")

# --- SIDEBAR (MONETIZATION) ---
with st.sidebar:
    st.header("💎 CareerMirror Pro")
    st.write("Get unlimited optimizations, cover letters, and LinkedIn makeovers.")
    st.link_button("Upgrade for $9/mo", "https://gumroad.com") # Replace with your link later
    st.divider()
    st.info("💡 **Tip:** Detailed inputs give better results.")

# --- SESSION STATE (The Memory) ---
if "optimized_text" not in st.session_state:
    st.session_state["optimized_text"] = ""
if "shared" not in st.session_state:
    st.session_state["shared"] = False

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    resume = st.text_area("Paste Your Resume", height=300, placeholder="Paste your current resume here...")
with col2:
    job = st.text_area("Paste Job Description", height=300, placeholder="Paste the job description here...")

# --- PDF GENERATOR FUNCTION ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Sanitize text to avoid encoding errors
    text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=text)
    return pdf.output(dest="S").encode("latin-1")

# --- ACTION AREA ---
st.markdown("###")

if st.button("✨ Optimize My Resume", type="primary"):
    if not resume or not job:
        st.warning("⚠️ Please fill in both text boxes.")
    else:
        with st.spinner("🤖 AI is rewriting your resume... (Takes ~5 seconds)"):
            try:
                payload = {"resume": resume, "jobDescription": job}
                response = requests.post(WORKER_URL, json=payload)
                
                if response.status_code == 200:
                    result_json = response.json()
                    
                    # Robust parsing logic
                    if "result" in result_json and "response" in result_json["result"]:
                        final_text = result_json["result"]["response"]
                    elif "response" in result_json:
                        final_text = result_json["response"]
                    else:
                        final_text = str(result_json)
                    
                    st.session_state["optimized_text"] = final_text
                    st.rerun() # Refresh to show result
                else:
                    st.error("Server Error. Please try again.")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- RESULT & VIRAL GATE ---
if st.session_state["optimized_text"]:
    st.markdown("---")
    st.subheader("✅ Your Optimized Resume")
    st.text_area("Copy/Edit Result:", value=st.session_state["optimized_text"], height=400)
    
    st.markdown("### 🔓 Unlock Download")
    st.write("To download this as a PDF, please share our tool or upgrade to Pro.")
    
    col_share, col_download = st.columns(2)
    
    with col_share:
        # THE VIRAL LOOP
        if st.button("📢 Share on LinkedIn (Unlocks PDF)"):
            st.session_state["shared"] = True
            js = "window.open('https://www.linkedin.com/sharing/share-offsite/?url=https://careermirror-app.streamlit.app')"
            st.components.v1.html(f"<script>{js}</script>", height=0)
            st.rerun()

    with col_download:
        if st.session_state["shared"]:
            # THE REWARD
            pdf_data = create_pdf(st.session_state["optimized_text"])
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_data,
                file_name="Optimized_Resume.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.button("⬇️ Download PDF (Locked)", disabled=True)
