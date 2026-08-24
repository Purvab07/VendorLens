import os

def document_loader(filepath:str) ->str:
    with open(filepath, 'r') as f:
        return f.read()

def chunk_text(text:str, chunk_size:int =500, overlap:int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def load_and_chunk(filepath:str) ->list[str]:
    text = document_loader(filepath)
    return chunk_text(text)

if __name__ == "__main__":
    test_file = 'data/regulations/cfpb_complaint_handling.txt'
    if os.path.exists(test_file):
        chunks = load_and_chunk(test_file)
        print(f"Loaded {len(chunks)} chunks")
        print("First chunk preview: ", chunks[0][:200])
    else:
        print(f"No file found at {test_file}. Please ensure the file exists.")