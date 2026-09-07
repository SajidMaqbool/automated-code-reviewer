import streamlit as st
import json
import urllib.request
import urllib.error

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Groq API")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "").strip()

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing in Streamlit Secrets!")
    else:
        with st.spinner("Analyzing code..."):
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
            
            # Active Production Models supported on Groq
            active_models = [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "qwen-2.5-coder-32b",
                "deepseek-r1-distill-llama-70b"
            ]
            
            success = False
            last_error = ""

            for model_name in active_models:
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
                        st.subheader(f"Model Review Feedback ({model_name})")
                        st.markdown(review_text)
                        success = True
                        break
                except urllib.error.HTTPError as e:
                    last_error = e.read().decode("utf-8")
                    # If model is deprecated or not found, try the next candidate
                    continue
                except Exception as e:
                    last_error = str(e)
                    continue

            if not success:
                st.error(f"Execution Error: {last_error}")
