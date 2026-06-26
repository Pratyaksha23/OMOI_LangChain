from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

from core.config import HF_TOKEN

llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    temperature=0.7,
    max_new_tokens=512
)

model = ChatHuggingFace(llm = llm)
