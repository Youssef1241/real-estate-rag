from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def chunk_documents(texts: list[str], filenames: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = [
        (chunk, filenames[i])
        for i, text in enumerate(texts)
        for chunk in text_splitter.split_text(text)
    ]
    documents = [Document(page_content=doc[0], metadata={"source": doc[1]}) for doc in documents] 
    return documents

