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
    return answer_question(q.question)

@app.post("/ask-stream")
def ask_stream(q: Question):
    stream, sources = answer_question_stream(q.question)

    def event_generator():
        for chunk in stream:
            if chunk.text:
                yield f"data: {json.dumps({'chunk': chunk.text})}\n\n"
        yield f"data: {json.dumps({'done': True, 'sources': sources})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")