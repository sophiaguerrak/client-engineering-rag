import pdfplumber
import os

pdf_path = "client-engineering-rag/assets/Unleashing the Power of AI  with IBM watsonxai.pdf"  

# Variable para almacenar todo el contenido
all_content = ""

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        # Extraer texto de la pagina
        page_text = page.extract_text()
        if page_text:
            all_content += f"\n{page_text}\n"

        # Extraer tablas de la pagina
        tables = page.extract_tables()
        if tables:
            for table_num, table in enumerate(tables, start=1):
                all_content += f"\n--- Table {table_num} from page {page_num} ---\n"
                for row in table:
                    row_text = " | ".join(
                        cell if cell else "" for cell in row)  
                    all_content += row_text + "\n"

# Guardamos el contenido en un archivo de texto
output_path = os.path.join(os.path.dirname(pdf_path), "document.txt")
with open(output_path, "w", encoding="utf-8") as file:
    file.write(all_content)

print("Extraction completed into 'document.txt'.")
