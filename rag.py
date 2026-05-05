from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config import VECTOR_PATH, MODEL_NAME

llm = OllamaLLM(model=MODEL_NAME)
emb = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(VECTOR_PATH, emb, allow_dangerous_deserialization=True)


def ask_law(query):
    docs = db.similarity_search(query, k=6)
    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
Use only the context. Cite sections & judgments.

CONTEXT:
{context}

QUESTION:
{query}
"""
    return llm(prompt)
