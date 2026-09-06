import os, glob
from dotenv import load_dotenv
from google import genai
import chromadb

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("college_docs")

def chunk_text(text, chunk_size=300, overlap=50):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def embed(text):
    result = client.models.embed_content(model="gemini-embedding-001", contents=text)
    return result.embeddings[0].values

def ingest():
    for filepath in glob.glob("data/*.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text)
        for idx, chunk in enumerate(chunks):
            embedding = embed(chunk)
            collection.add(
                ids=[f"{os.path.basename(filepath)}-{idx}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": os.path.basename(filepath)}]
            )
        print(f"Ingested {filepath} ({len(chunks)} chunks)")

if __name__ == "__main__":
    ingest()