
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

app = FastAPI(title="AI Code Reviewer API")

# Request schema
class CodeReviewRequest(BaseModel):
    instruction: str = "Review this code for security vulnerabilities, bugs, or improvements."
    code: str

# Global model variables
MODEL_NAME = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
LORA_PATH = "./final_code_reviewer_lora"

tokenizer = None
model = None

@app.on_event("startup")
def load_model():
    global tokenizer, model
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    model = PeftModel.from_pretrained(base_model, LORA_PATH)
    model.eval()

@app.post("/review")
def generate_review(request: CodeReviewRequest):
    prompt = f"<|im_start|>system\nYou are an expert AI Code Reviewer.<|im_end|>\n<|im_start|>user\n{request.instruction}\n\nCode:\n{request.code}<|im_end|>\n<|im_start|>assistant\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            do_sample=True,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.2,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    review_output = response.split("assistant\n")[-1]
    
    return {"review": review_output}
