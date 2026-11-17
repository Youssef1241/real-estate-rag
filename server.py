from mcp.server.mcpserver import MCPServer
from retrieve import create_bm25_retriever, create_vector_store, retrieve_hybrid_chunks
from dotenv import load_dotenv
from verifier import verify_answers
load_dotenv()
mcp = MCPServer("rag-docs")
sparse = create_bm25_retriever()
vector_store = create_vector_store()
@mcp.tool()
def search_documents(query: str, k: int = 10) -> list[dict]:
    """
    Retrieve the relevant documents for a query.
    Args:
        query: The query to retrieve documents for
        k: The number of documents to retrieve (default: 10)
    """
    try:
        results = retrieve_hybrid_chunks(query, sparse, vector_store, k)
    except Exception as e:
        return [{"error": str(e)}]
    return [{
        "page_content": doc.page_content,
        "chunk_id": doc.metadata['chunk_id'],
        "source": doc.metadata['source']
    } for doc in results]

@mcp.tool()
def verify_citations(answers: list) -> list[dict]:
    """
    Verify the model's citations.
    Args:
        answers: list of statement-source pairs with "statement" and "source" keys. "source" contains the chunk_id metadata field from the chunk list
    Returns:
        list of statement-verdict pairs with "statement" (str) and "verdict" (bool) keys
    """
    try:
        results = verify_answers(answers, vector_store)
    except Exception as e:
        return [{"statement": str(e), "verdict": False}]
    if not results:
        return [{"statement": "One or more chunks not referenced", "verdict": False}]
    return [
        {
            "statement": result.statement,
            "verdict": result.verdict,
        }
        for result in results.verdicts
    ]     
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="localhost", port=8001)
