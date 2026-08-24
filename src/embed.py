import chromadb
from src.ingest import load_and_chunk

client = chromadb.PersistentClient(path='./chroma_db')

def get_collection(name:str='documents'):
    return client.get_or_create_collection(name=name)

def add_documents(filepath:str, source_label:str, collection_name:str='documents'):
    collection = get_collection(collection_name)
    chunks = load_and_chunk(filepath)
    ids = [f"{source_label}_{i}" for i in range(len(chunks))]
    metadatas = [{"source":source_label, "chunk_index":i} for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)

    print(f"Added {len(chunks)} documents to collection '{collection_name}' from source '{source_label}'.")

def search(query:str, collection_name:str='documents', n_results:int=3):
    
