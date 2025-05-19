import os
import sqlite3
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
import json

load_dotenv()
api_key = os.getenv("WATSONX_APIKEY")
url = os.getenv("WATSONX_URL")
project_id = os.getenv("WATSONX_PROJECT_ID")

credentials = Credentials(
    url=url,
    api_key=api_key
)

embed_params = {
    EmbedParams.TRUNCATE_INPUT_TOKENS: 3,
    EmbedParams.RETURN_OPTIONS: {
        'input_text': True
    }
}

embedding_model = Embeddings(
    model_id="ibm/slate-30m-english-rtrvr-v2",
    params=embed_params,
    credentials=credentials,
    project_id=project_id
)

# Conectamos a la db
conn = sqlite3.connect("chunks.db")
cur = conn.cursor()

# Leemos los chunks
cur.execute("SELECT id, chunk_text FROM chunks WHERE embedding IS NULL")
rows = cur.fetchall()

print(f"Generando embeddings para {len(rows)} chunks...")

# Generamos y guardamos embeddings en la db
for chunk_id, chunk_text in rows:
    try:
        print(f"Generando embedding para el chunk {chunk_id}")
        result = embedding_model.embed_documents([chunk_text])
        vector = result[0]
        vector_str = json.dumps(vector)
        cur.execute("UPDATE chunks SET embedding = ? WHERE id = ?", (vector_str, chunk_id))
    except Exception as e:
        print(f"Error con chunk {chunk_id}: {e}")

conn.commit()
conn.close()

print("Embeddings generados y guardados correctamente.")