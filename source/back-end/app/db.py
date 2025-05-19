import sqlite3
import json
import os
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
import chromadb

load_dotenv()
api_key = os.getenv("WATSONX_APIKEY")
url = os.getenv("WATSONX_URL")
project_id = os.getenv("WATSONX_PROJECT_ID")

credentials = Credentials(url=url, api_key=api_key)

embed_params = {
    EmbedParams.TRUNCATE_INPUT_TOKENS: 3,
    EmbedParams.RETURN_OPTIONS: {'input_text': True}
}

embedding_model = Embeddings(
    model_id="ibm/slate-30m-english-rtrvr-v2",
    params=embed_params,
    credentials=credentials,
    project_id=project_id
)

DB_PATH = os.path.join(os.path.dirname(__file__), "chunks.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id TEXT NOT NULL,
        sender TEXT NOT NULL,
        text TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
''')
conn.commit()
print("Table 'chat_messages' was successfully created.")
conn.close()

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'chunks.json')
with open(json_path, 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print("Generating embeddings with Watsonx...")
embeddings = embedding_model.embed_documents(chunks)

chroma_client = chromadb.PersistentClient(path="./chroma")
collection = chroma_client.get_or_create_collection("chunks_collection")

ids = [f"chunk_{i}" for i in range(len(chunks))]
collection.add(
    documents=chunks,
    embeddings=embeddings,
    ids=ids
)

print(f"{len(chunks)} chunks inserted in ChromaDB.")