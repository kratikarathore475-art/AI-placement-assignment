from rag.loaders import load_pdf
from rag.chunker import split_text


pdf_path = "data/raw/placement_notes.pdf"

text = load_pdf(pdf_path)

chunks = split_text(text)

print("Total characters:", len(text))
print("Total chunks:", len(chunks))

print("\n--- FIRST CHUNK ---")
print(chunks[0])

print("\n--- SECOND CHUNK ---")
print(chunks[1])