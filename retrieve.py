from clients import make_vector_store_client, make_embedding_client, make_llm_client
from langchain_community.retrievers import BM25Retriever
from chunker import prepare_documents
from loader import load_txt, add_chunk_ids
from prompts import REWORD_USER_PROMPT, REWORD_SYSTEM_PROMPT
import re
import os

def create_vector_store(k=10):
    embeddings = make_embedding_client()
    vector_store = make_vector_store_client(embeddings)
    return vector_store

def reword_query(query):
    model = make_llm_client()
    response = model.invoke(REWORD_SYSTEM_PROMPT + REWORD_USER_PROMPT.format(query=query))
    return response.content

def tokenize(text):
    return re.findall(r"\w+", text)

def create_bm25_retriever(k=10, input_dir="texts"):
    minimum_chunk_size = 500
    maximum_chunk_size = 1000
    chunk_overlap = 150
    outlier_chunk_size = 100
    files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt')]
    filenames = [filepath.split('/')[-1] for filepath in files]
    texts = [load_txt(filepath) for filepath in files]
    documents = prepare_documents(texts, filenames, minimum_chunk_size, maximum_chunk_size, chunk_overlap, outlier_chunk_size)
    documents = add_chunk_ids(documents)
    bm25 = BM25Retriever.from_documents(documents, preprocess_func=tokenize, k=k)
    return bm25

def weighted_rrf(rank_lists, weights, k=60):
    """rank_lists: list of lists of Documents, each ordered best-first.
    weights: one weight per list. Returns fused Documents, best-first."""
    scores, docs_by_key = {}, {}
    for ranking, w in zip(rank_lists, weights):
        for rank, doc in enumerate(ranking):
            key = doc.metadata.get("chunk_id") or doc.id or doc.page_content
            docs_by_key[key] = doc
            scores[key] = scores.get(key, 0) + w * (1 / (k + rank + 1))
    ordered = sorted(scores, key=scores.get, reverse=True)
    return [docs_by_key[key] for key in ordered]


def dedupe_by_chunk_id(docs):
    seen = set()
    unique = []
    for doc in docs:
        chunk_id = doc.metadata.get("chunk_id")
        if chunk_id is not None:
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
        unique.append(doc)
    return unique

def retrieve_hybrid_chunks(query: str, sparse, vector_store, k=10):
    sparse_results = sparse.invoke(query)
    dense = vector_store.as_retriever(search_kwargs={"k": k})
    reworded_query = reword_query(query)
    print(reworded_query)
    dense_results = dense.invoke(reworded_query)
    results = weighted_rrf([sparse_results, dense_results], weights=[0.6, 0.4])
    results = dedupe_by_chunk_id(results)[:k]
    return results

