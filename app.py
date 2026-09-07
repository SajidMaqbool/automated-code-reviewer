import streamlit as st
import requests

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Fine-Tuned Qwen2.5-Coder-1.5B via Hugging Face API")

API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"

# Safely load token ONLY from Streamlit Secrets
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    elif not HF_TOKEN:
        st.error("HF_TOKEN not found in Streamlit Secrets. Please configure it in your app settings.")
    else:
        with st.spinner("Analyzing code via Hugging Face Inference..."):
            headers = {
                "Authorization": f"Bearer {HF_TOKEN.strip()}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "Baghiii/qwen2.5-coder-lora-reviewer",
                "messages": [
                    {"role": "system", "content": "You are an expert code reviewer."},
                    {"role": "user", "content": f"Instruction: {instruction}\nCode:\n{code_input}"}
                ],
                "max_tokens": 512
            }
            
            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    review_text = result["choices"][0]["message"]["content"]
                    st.subheader("Model Review Feedback")
                    st.markdown(review_text)
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
