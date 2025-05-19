import os
import sqlite3
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
import chromadb

load_dotenv()
api_key = os.getenv("WATSONX_APIKEY")
url = os.getenv("WATSONX_URL")
project_id = os.getenv("WATSONX_PROJECT_ID")

credentials = Credentials(url=url, api_key=api_key)

embedding_model = Embeddings(
    model_id="ibm/slate-30m-english-rtrvr-v2",
    params={
        EmbedParams.TRUNCATE_INPUT_TOKENS: 3,
        EmbedParams.RETURN_OPTIONS: {'input_text': True}
    },
    credentials=credentials,
    project_id=project_id
)

generation_model = ModelInference(
    model_id="ibm/granite-13b-instruct-v2",
    credentials=credentials,
    project_id=project_id,
    params={
        GenParams.MAX_NEW_TOKENS: 700,
        GenParams.DECODING_METHOD: "greedy",
    }
)

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection("chunks")


def save_message(chat_id: str, sender: str, text: str):
    """Saves a message into the database"""
    DB_PATH = os.path.join(os.path.dirname(__file__), "chunks.db")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO chat_messages (chat_id, sender, text) VALUES (?, ?, ?)
    ''', (chat_id, sender, text))
    conn.commit()
    conn.close()

def ask_question(user_question: str, chat_id: str) -> str:
    """Generates a response"""
    save_message(chat_id, "user", user_question)
    question_vector = embedding_model.embed_documents([user_question])[0]

    results = collection.query(
        query_embeddings=[question_vector],
        n_results=3
    )
    top_chunks = results["documents"][0]
    contexto = "\n\n".join(top_chunks)
    prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.

Context:
{contexto}


User: 
{user_question}

"""

    response = generation_model.generate_text(prompt)
    save_message(chat_id, "user", user_question)
    save_message(chat_id, "bot", response)

    return response