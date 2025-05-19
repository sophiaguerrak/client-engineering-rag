from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.rag import ask_question
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API funcionando"}

class QuestionRequest(BaseModel):
    question: str
    chat_id: int

@app.post("/ask")
def ask(request: QuestionRequest):
    try:
        response = ask_question(request.question, request.chat_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class ChatMessage(BaseModel):
    chat_id: int
    sender: str
    text: str

@app.post("/messages")
def save_message(msg: ChatMessage):
    DB_PATH = os.path.join(os.path.dirname(__file__), "chunks.db")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_messages (chat_id, sender, text) VALUES (?, ?, ?)",
        (msg.chat_id, msg.sender, msg.text)
    )
    conn.commit()
    conn.close()
    return {"status": "Message saved"}

@app.get("/messages")
def get_messages():
    DB_PATH = os.path.join(os.path.dirname(__file__), "chunks.db")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT chat_id, sender, text, timestamp FROM chat_messages ORDER BY timestamp ASC")
    rows = cur.fetchall()
    conn.close()
    return [{"chat_id": r[0], "sender": r[1], "text": r[2], "timestamp": r[3]} for r in rows]

@app.delete("/messages/{chat_id}")
def delete_chat(chat_id: int):
    DB_PATH = os.path.join(os.path.dirname(__file__), "chunks.db")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_messages WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    return {"message": f"Chat {chat_id} deleted"}