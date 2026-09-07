import streamlit as st
from huggingface_hub import InferenceClient

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Fine-Tuned Qwen2.5-Coder-1.5B via Hugging Face")

HF_TOKEN = st.secrets.get("HF_TOKEN", "").strip()

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    elif not HF_TOKEN:
        st.error("HF_TOKEN missing in Streamlit Secrets!")
    else:
        with st.spinner("Analyzing code via Hugging Face..."):
            try:
                client = InferenceClient(
                    model="Baghiii/qwen2.5-coder-lora-reviewer",
                    token=HF_TOKEN
                )
                
                prompt = f"<|im_start|>system\nYou are an expert code reviewer.<|im_end|>\n<|im_start|>user\nInstruction: {instruction}\nCode:\n{code_input}<|im_end|>\n<|im_start|>assistant\n"
                
                response = client.text_generation(
                    prompt,
                    max_new_tokens=512,
                    return_full_text=False
                )
                
                st.subheader("Model Review Feedback")
                st.markdown(response)
                
            except Exception as e:
                st.error(f"Inference Error: {e}")
