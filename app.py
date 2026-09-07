import streamlit as st
import requests

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Qwen2.5-Coder-1.5B (QLoRA Fine-Tuned)")

instruction = st.text_input("Review Instruction", "Review this Python snippet for vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code", height=200, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid code.")
    else:
        with st.spinner("Analyzing code..."):
            try:
                res = requests.post("http://127.0.0.1:8000/review", json={"instruction": instruction, "code": code_input})
                if res.status_code == 200:
                    st.subheader("Model Review Feedback")
                    st.markdown(res.json()["review"])
                else:
                    st.error(f"Error {res.status_code}: {res.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}")
