import streamlit as st
import requests

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Fine-Tuned Qwen2.5-Coder-1.5B via Hugging Face API")

# Direct Model Inference API Endpoint
API_URL = "https://api-inference.huggingface.co/models/Baghiii/qwen2.5-coder-lora-reviewer"
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    elif not HF_TOKEN:
        st.error("HF_TOKEN missing in Streamlit Secrets! Please add your Hugging Face token in app settings.")
    else:
        with st.spinner("Analyzing code via Hugging Face Inference..."):
            prompt = f"<|im_start|>system\nYou are an expert code reviewer.<|im_end|>\n<|im_start|>user\nInstruction: {instruction}\nCode:\n{code_input}<|im_end|>\n<|im_start|>assistant\n"
            
            headers = {
                "Authorization": f"Bearer {HF_TOKEN.strip()}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 512,
                    "return_full_text": False
                }
            }
            
            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        review_text = result[0].get("generated_text", "")
                        st.subheader("Model Review Feedback")
                        st.markdown(review_text)
                    else:
                        st.write(result)
                elif response.status_code == 503:
                    st.info("Model currently loading on Hugging Face servers. Please wait 20 seconds and click Analyze again!")
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
