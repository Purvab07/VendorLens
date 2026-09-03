import chromadb
from src.ingest import load_and_chunk

client = chromadb.PersistentClient(path='./chroma_db')

def get_collections(name: str = 'documents'):
    return client.get_or_create_collection(name=name)

def add_documents(filepath: str, source_label: str, collection_name: str = 'documents'):
    collection = get_collections(collection_name)
    chunks = load_and_chunk(filepath)
    ids = [f"{source_label}_{i}" for i in range(len(chunks))]
    metadatas = [{'source': source_label, 'chunk_index': i} for i in range(len(chunks))]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    print(f"Added {len(chunks)} in collection {collection_name} from source {source_label}")

def search(query: str, collection_name: str = 'documents', n_results: int = 3):
    collection = get_collections(collection_name)
    results = collection.query(query_texts=[query], n_results=n_results)
    return results

if __name__ == "__main__":
    add_documents(
        filepath="data/regulations/cfpb_complaint_handling.txt",
        source_label="cfpb_complaint_handling"
    )
    results = search("How should a company handle customer complaints?")
    print("\nTop matching chunk:")
    print(results["documents"][0][0])