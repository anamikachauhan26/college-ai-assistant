import os
from dotenv import load_dotenv
from google import genai
import chromadb

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("college_docs")

SYSTEM_PROMPT = """You are a friendly, helpful assistant chatbot for Walchand College of Engineering students.
Answer naturally and conversationally, like a knowledgeable senior student helping a junior — not like a search engine reading a document out loud.
Use ONLY the context below. Do not use any outside knowledge.
If the context does not contain the answer, say something natural like "I don't have that information right now — you might want to check the official notice board or contact the department directly."
Never mention file names, documents, or internal sources when you don't know something — just say you don't have it."""

def embed(text):
    result = client.models.embed_content(model="gemini-embedding-001", contents=text)
    return result.embeddings[0].values

def retrieve(question, top_k=3):
    q_embedding = embed(question)
    results = collection.query(query_embeddings=[q_embedding], n_results=top_k)
    contexts = results["documents"][0]
    sources = list(dict.fromkeys(m["source"] for m in results["metadatas"][0]))  # dedupe, keep order
    return contexts, sources

def build_prompt(question, contexts):
    context_block = "\n\n".join(contexts)
    return f"""{SYSTEM_PROMPT}

Context:
{context_block}

Question: {question}
Answer:"""

def answer_question(question, top_k=3):
    contexts, sources = retrieve(question, top_k)
    prompt = build_prompt(question, contexts)
    response = client.models.generate_content(model="gemini-flash-latest", contents=prompt)
    return {"answer": response.text, "sources": sources}

def answer_question_stream(question, top_k=3):
    contexts, sources = retrieve(question, top_k)
    prompt = build_prompt(question, contexts)
    stream = client.models.generate_content_stream(model="gemini-flash-latest", contents=prompt)
    return stream, sources