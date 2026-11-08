import time
from tqdm import tqdm
from clients import make_embedding_client, make_vector_store_client
def embed_documents(documents: list[str]) -> list[str]:
    embeddings = make_embedding_client()
    vector_store = make_vector_store_client(embeddings)

    batch_size = 20
    for i in tqdm(range(0, len(documents), batch_size)):
        batch = documents[i:i+batch_size]
        vector_store.add_documents(batch)
        if i + batch_size < len(documents):
            time.sleep(5)