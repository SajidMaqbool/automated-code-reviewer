import streamlit as st
import requests

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Fine-Tuned Qwen2.5-Coder-1.5B (QLoRA)")

# Instruction & Input fields
instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

# Web execution call
if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please provide valid source code.")
    else:
        st.info("To perform live analysis, connect this UI to your running FastAPI backend server instance.")
        st.code(f"Instruction: {instruction}\nTarget Code:\n{code_input}", language="python")
