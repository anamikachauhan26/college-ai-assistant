import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rag import answer_question, answer_question_stream

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Question):
    try:
        return answer_question(q.question)
    except Exception as e:
        print(f"ERROR in /ask: {e}")
        return {"answer": "Sorry, something went wrong on my end. Please try again in a moment.", "sources": []}

@app.post("/ask-stream")
def ask_stream(q: Question):
    try:
        stream, sources = answer_question_stream(q.question)
    except Exception as e:
        print(f"ERROR in /ask-stream: {e}")
        def error_gen():
            yield f"data: {json.dumps({'chunk': 'Sorry, something went wrong. Please try again.'})}\n\n"
            yield f"data: {json.dumps({'done': True, 'sources': []})}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")

    def event_generator():
        for chunk in stream:
            if chunk.text:
                yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
        yield f"data: {json.dumps({'done': True, 'sources': sources})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")