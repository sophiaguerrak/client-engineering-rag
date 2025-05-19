from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

# Lee el texto
ruta_archivo = "client-engineering-rag/assets/document.txt"
with open(ruta_archivo, "r", encoding="utf-8") as file:
    texto_completo = file.read()

# Crear el splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""]
)

# Generar los chunks
chunks = splitter.split_text(texto_completo)

# Ver algunos chunks para confirmar
for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i+1} ---\n{chunk}")

with open("client-engineering-rag/source/back-end/app/chunks.json", "w", encoding="utf-8") as json_file:
    json.dump(chunks, json_file, ensure_ascii=False, indent=4)

print("Chunks saved in 'chunks.json'.")

