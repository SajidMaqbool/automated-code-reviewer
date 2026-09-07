import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

st.set_page_config(page_title="AI Code Reviewer", layout="wide")
st.title("⚡ AI-Driven Code Review Assistant")
st.caption("Powered by Fine-Tuned Qwen2.5-Coder-1.5B (LoRA Adapter)")

@st.cache_resource
def load_model():
    base_model_name = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
    adapter_name = "Baghiii/qwen2.5-coder-lora-reviewer"
    
    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None
    )
    model = PeftModel.from_pretrained(base_model, adapter_name)
    return tokenizer, model

instruction = st.text_input("Review Instruction", "Review this Python code snippet for security vulnerabilities or anti-patterns.")
code_input = st.text_area("Paste Python Code / Diff", height=220, value="import os\ndef connect():\n    db_pass = '123456_secret'\n    return db_pass")

if st.button("Analyze Code", type="primary"):
    if not code_input.strip():
        st.warning("Please enter valid source code.")
    else:
        with st.spinner("Loading model and generating code review..."):
            try:
                tokenizer, model = load_model()
                
                messages = [
                    {"role": "system", "content": "You are an expert code reviewer."},
                    {"role": "user", "content": f"Instruction: {instruction}\nCode:\n{code_input}"}
                ]
                
                prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = tokenizer(prompt, return_tensors="pt")
                
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                outputs = model.generate(**inputs, max_new_tokens=512)
                response_text = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
                
                st.subheader("Model Review Feedback")
                st.markdown(response_text)
                
            except Exception as e:
                st.error(f"Execution Error: {e}")
