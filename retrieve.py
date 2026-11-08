from clients import make_vector_store_client, make_embedding_client, make_llm_client
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
import re

def create_vector_store_retriever(k=10):
    embeddings = make_embedding_client()
    vector_store = make_vector_store_client(embeddings)
    dense = vector_store.as_retriever(search_kwargs={"k": k})
    return dense

def reword_query(query):
    SYSTEM_PROMPT = """
    You are a helpful assistant that rewords a query to be more specific and accurate. You are given a question and you must return keywords that will help search for documents in a vector store. The query will be in arabic, so return the keywords in arabic.
    """
    USER_PROMPT = f"""
    Query: {query}
    Reworded Keywords:
    """
    model = make_llm_client()
    response = model.invoke(SYSTEM_PROMPT + USER_PROMPT)
    return response.content

def reword_and_retrieve_test(query, k=5):
    reworded_query = reword_query(query)
    print("Reworded Query: ", reworded_query)
    retrieved_documents = create_vector_store_retriever(reworded_query)
    return retrieved_documents

def tokenize(text):
    return re.findall(r"\w+", text)

def create_bm25_retriever(documents, k=10):
    bm25 = BM25Retriever.from_documents(documents, preprocess_func=tokenize, k=k)
    return bm25

def weighted_rrf(rank_lists, weights, k=60):
    """rank_lists: list of lists of Documents, each ordered best-first.
    weights: one weight per list. Returns fused Documents, best-first."""
    scores, docs_by_key = {}, {}
    for ranking, w in zip(rank_lists, weights):
        for rank, doc in enumerate(ranking):
            key = doc.metadata.get("id") or doc.page_content  # stable identity
            docs_by_key[key] = doc
            scores[key] = scores.get(key, 0) + w * (1 / (k + rank + 1))
    ordered = sorted(scores, key=scores.get, reverse=True)
    return [docs_by_key[key] for key in ordered]

def retrieve_hybrid_chunks(query: str, k=10):
    dense = create_vector_store_retriever(k=k)
    sparse = create_bm25_retriever(k=k)
    sparse_results = sparse.invoke(query)
    dense_results = dense.invoke(reword_query(query))
    results = weighted_rrf([sparse_results, dense_results], weights=[1, 1])[:10]
    return results

