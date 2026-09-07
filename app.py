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
        with st.spinner("Fetching active models & analyzing code..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
            
            # Step 1: Fetch list of models available to YOUR API key dynamically
            active_model = None
            try:
                models_req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers=headers, method="GET")
                with urllib.request.urlopen(models_req) as response:
                    models_data = json.loads(response.read().decode("utf-8"))
                    available_models = [m["id"] for m in models_data.get("data", [])]
                    
                    # Filter for active LLM text completion models
                    text_models = [m for m in available_models if "whisper" not in m and "safetensors" not in m]
                    if text_models:
                        active_model = text_models[0]
            except Exception as e:
                st.warning(f"Could not fetch models dynamically: {e}")
            
            # Fallback if listing models fails
            if not active_model:
                active_model = "llama-3.1-8b-instant"

            # Step 2: Make the code review call with the guaranteed active model
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": active_model,
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
                    st.subheader(f"Model Review Feedback (Using: {active_model})")
                    st.markdown(review_text)
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                st.error(f"HTTP Error {e.code}: {err_body}")
            except Exception as e:
                st.error(f"Execution Error: {e}")
