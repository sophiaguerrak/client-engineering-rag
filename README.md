# Chat RAG API

This is a simple FastAPI backend that handles a local RAG (Retrieval-Augmented Generation) workflow. The project uses a local SQLite database to store and retrieve messages in a chat format, and ChromaDB to store the embedding vectors. There's also a frontend built with React that connects to this API to display the chat interface.

## Requirements
	•	Docker
	•	Python 3.11+ 
	•	A .env file with the API credentials in source/back-end/.env

## How to Run

You can either run everything through Docker (recommended), or manually if needed.

⸻

## Running with Docker
	1.	Navigate to the source/back-end folder.
	2.	Make sure you have your .env file with the proper keys (OpenAI, etc.) in the source/back-end/ directory.
	3.	Before running the app, you must initialize the database. Run this:

cd source/back-end/app
python db.py

	4.	Now, go back to source/back-end and build the Docker image:

docker build -t rag-api .

	5.	Run the container:

docker run -p 8000:8000 rag-api

The API will be available at http://localhost:8000.

⸻

## Manually (for dev or debugging)
	1.	Install dependencies:

cd source/back-end
pip install -r requirements.txt

	2.	Make sure the .env file exists in the same folder (source/back-end/.env).
	3.	Initialize the database:

cd app
python db.py

	4.	Run the server:

uvicorn main:app --reload


⸻

## Notes
	•	If you modify the Dockerfile, you’ll need to rebuild the image:

docker build -t rag-api .

	•	Make sure the database file chunks.db is created inside the app/ folder. That’s where the backend looks for it.
	•	You can test the API with a tool like Postman or from your frontend at http://localhost:5173.