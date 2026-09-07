import streamlit as st
import requests

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Fine-Tuned Qwen2.5-Coder-1.5B via Hugging Face API")

# Updated API Endpoint URL with Baghiii repository
API_URL = "https://api-inference.huggingface.co/models/Baghiii/qwen2.5-coder-lora-reviewer"
HF_TOKEN = st.secrets.get("HF_TOKEN", "")

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    else:
        with st.spinner("Analyzing code via Hugging Face Inference..."):
            prompt = f"<|im_start|>system\nYou are an expert code reviewer.<|im_end|>\n<|im_start|>user\nInstruction: {instruction}\nCode:\n{code_input}<|im_end|>\n<|im_start|>assistant\n"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}
            
            try:
                response = requests.post(API_URL, headers=headers, json={"inputs": prompt, "parameters": {"max_new_tokens": 512}})
                if response.status_code == 200:
                    result = response.json()
                    review_text = result[0]["generated_text"].split("<|im_start|>assistant\n")[-1]
                    st.subheader("Model Review Feedback")
                    st.markdown(review_text)
                else:
                    st.error(f"API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
