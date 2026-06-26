from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from core.config import HF_TOKEN
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILE_PATH = os.path.join(BASE_DIR, "data", "vectorstore")

embedding = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2"
)

_vectorstore = None

def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(persist_directory=FILE_PATH, embedding_function=embedding)
    return _vectorstore

def clear_memory():
    global _vectorstore
    vs = _get_vectorstore()
    vs.delete_collection()   # Chroma cleans up its own files/handles
    _vectorstore = None      # force a fresh client on next use

def add_entry(text):
    _get_vectorstore().add_texts([text])

def get_related_entries(query):
    return _get_vectorstore().similarity_search(query, k=3)