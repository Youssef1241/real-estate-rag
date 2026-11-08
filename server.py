from mcp.server.mcpserver import MCPServer
from retrieve import retrieve_documents
from dotenv import load_dotenv
load_dotenv()
mcp = MCPServer("rag-docs")

@mcp.tool()
def search_documents(query: str, k: int = 5) -> list[dict]:
    """
    Retrieve the relevant documents for a query.
pl
    Args:
        query: The query to retrieve documents for
        k: The number of documents to retrieve (default: 5)
    """
    try:
        results = retrieve_documents(query, k)
    except Exception as e:
        return f"Error: {e}"
    return [
        {
            "text": result.page_content,
            "source-file": result.metadata["source"],
        }
        for result in results
    ] 
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="localhost", port=8000)