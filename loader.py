import hashlib

def load_txt(path: str) -> str:
    with open(path, "r") as f:
        return f.read()

def add_chunk_ids(documents):
    for i, doc in enumerate(documents):
        source = doc.metadata.get("source", "")
        digest = hashlib.md5(f"{source}|{i}|{doc.page_content}".encode()).hexdigest()[:12]
        doc.metadata["chunk_id"] = digest
    return documents
