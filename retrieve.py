from clients import make_vector_store_client, make_embedding_client
def retrieve_documents(query, k=5):
    embeddings = make_embedding_client()
    vector_store = make_vector_store_client(embeddings)
    return vector_store.similarity_search(query, k=k)