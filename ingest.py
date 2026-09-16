import os, glob, time
from dotenv import load_dotenv
from google import genai
from google.genai import errors
import chromadb
from urllib.parse import unquote

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

def embed(text, retries=5):
    for attempt in range(retries):
        try:
            result = client.models.embed_content(model="gemini-embedding-001", contents=text)
            return result.embeddings[0].values
        except errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" in str(e) and attempt < retries - 1:
                wait = 15 * (attempt + 1)
                print(f"Rate limited, waiting {wait}s before retry...")
                time.sleep(wait)
            else:
                raise

def make_readable_title(filepath):
    name = os.path.basename(filepath).replace(".txt", "")
    parts = name.split("_", 2)
    slug = parts[2] if parts[0] in ("notice", "page") and len(parts) == 3 else name
    slug = unquote(slug)
    title = slug.replace("-", " ").replace("_", " ").strip()
    return title.title() if title.isascii() else "College Notice"

def ingest():
    existing_ids = set(collection.get()["ids"])  # skip chunks already ingested
    for filepath in glob.glob("data/*.txt"):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = chunk_text(text)
        readable_title = make_readable_title(filepath)
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{os.path.basename(filepath)}-{idx}"
            if chunk_id in existing_ids:
                continue  # already embedded, don't waste quota re-doing it
            embedding = embed(chunk)
            collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": readable_title}]
            )
            time.sleep(1.5)  # stay under free-tier rate limit
        print(f"Ingested {filepath} as '{readable_title}' ({len(chunks)} chunks)")

if __name__ == "__main__":
    ingest()