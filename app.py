import streamlit as st
import json
import urllib.request
import urllib.error

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Groq API")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "").strip()

# User can choose models directly from UI or type custom ones if Groq updates them
selected_model = st.selectbox(
    "Select Groq Model",
    options=[
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "qwen-2.5-coder-32b",
        "Custom Model Entry..."
    ]
)

if selected_model == "Custom Model Entry...":
    model_name = st.text_input("Enter Active Model ID manually", value="llama-3.3-70b-versatile")
else:
    model_name = selected_model

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing in Streamlit Secrets!")
    else:
        with st.spinner(f"Analyzing code using {model_name}..."):
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
            
            payload = {
                "model": model_name,
                "messages": [
                    {"role": "system", "content": "You are an expert AI Code Reviewer specializing in security and performance."},
                    {"role": "user", "content": f"Instruction: {instruction}\n\nCode:\n{code_input}"}
                ],
                "temperature": 0.2,
                "max_tokens": 1024
            }
            
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            
            try:
                with urllib.request.urlopen(req) as response:
                    res_body = response.read().decode("utf-8")
                    result = json.loads(res_body)
                    review_text = result["choices"][0]["message"]["content"]
                    st.success(f"Successfully reviewed with model: {model_name}")
                    st.subheader("Model Review Feedback")
                    st.markdown(review_text)
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                st.error(f"HTTP Error {e.code}: {err_body}")
            except Exception as e:
                st.error(f"Execution Error: {e}")
