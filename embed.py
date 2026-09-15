from clients import make_embedding_client, make_vector_store_client
def embed_documents(documents: list[str]) -> list[str]:
    embeddings = make_embedding_client()
    vector_store = make_vector_store_client(embeddings)
    vector_store.add_documents(documents)