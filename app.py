import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Groq Cloud Official SDK")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "").strip()

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    elif not GROQ_API_KEY:
        st.error("GROQ_API_KEY missing in Streamlit Secrets!")
    else:
        with st.spinner("Analyzing code via Groq..."):
            try:
                # Initialize Official Client
                client = Groq(api_key=GROQ_API_KEY)
                
                # Dynamic Model Selection from User's Account Scope
                available_models = [m.id for m in client.models.list().data]
                selected_model = available_models[0] if available_models else "llama-3.1-8b-instant"
                
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": "You are an expert AI Code Reviewer specializing in security and optimization."},
                        {"role": "user", "content": f"Instruction: {instruction}\n\nCode:\n{code_input}"}
                    ],
                    temperature=0.2,
                    max_tokens=1024
                )
                
                review_text = response.choices[0].message.content
                st.subheader(f"Model Review Feedback ({selected_model})")
                st.markdown(review_text)
                
            except Exception as e:
                st.error(f"Execution Error: {e}")
