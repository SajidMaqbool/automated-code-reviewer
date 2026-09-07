import streamlit as st
import requests

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Groq API")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "").strip()
API_URL = "https://api.groq.com/openai/v1/chat/completions"

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing in Streamlit Secrets!")
    else:
        with st.spinner("Analyzing code..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Active Groq Models List (Fallback strategy)
            models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
            
            success = False
            for model_id in models_to_try:
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": "You are an expert AI Code Reviewer specializing in security and performance."},
                        {"role": "user", "content": f"Instruction: {instruction}\n\nCode:\n{code_input}"}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 1024
                }
                
                try:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        review_text = result["choices"][0]["message"]["content"]
                        st.subheader(f"Model Review Feedback ({model_id})")
                        st.markdown(review_text)
                        success = True
                        break
                except Exception:
                    continue
            
            if not success:
                st.error("API Request failed across available models. Please verify your GROQ_API_KEY in Streamlit Secrets.")
