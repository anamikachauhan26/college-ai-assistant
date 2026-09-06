import os
from dotenv import load_dotenv
from google import genai
import chromadb

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("college_docs")

def embed(text):
    result = client.models.embed_content(model="gemini-embedding-001", contents=text)
    return result.embeddings[0].values

def answer_question(question, top_k=3):
    q_embedding = embed(question)
    results = collection.query(query_embeddings=[q_embedding], n_results=top_k)
    contexts = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]

    context_block = "\n\n".join(contexts)
    prompt = f"""You are a college assistant. Answer the question using ONLY the context below.
If the answer isn't in the context, say you don't have that information.

Context:
{context_block}

Question: {question}
Answer:"""

    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=prompt
    )
    return {"answer": response.text, "sources": list(set(sources))}