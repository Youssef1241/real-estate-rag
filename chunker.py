from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import re
import json
SEPARATOR_TOKEN = "<SEP>"
def chunk_documents(texts: list[str], filenames: list[str], chunk_size: int, chunk_overlap: int) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = [
        (chunk, filenames[i])
        for i, text in enumerate(texts)
        for chunk in text_splitter.split_text(text)
    ]
    documents = [Document(page_content=doc[0], metadata={"source": doc[1]}) for doc in documents] 
    return documents

def chunk_by_article(text: str, pattern: str, min_chars: int, max_chars: int, chunk_overlap: int) -> list:
    chunks = []
    split_documents = re.split(pattern, text, flags=re.MULTILINE)
    splitter = RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=chunk_overlap)
    chunk_idx = 0
    for article in split_documents:
        if chunk_idx >= len(split_documents):
            break
        if len(split_documents[chunk_idx]) > max_chars:
            oversized = splitter.split_text(split_documents[chunk_idx])
            if chunk_idx != 0:
                header = oversized[0].partition("\n")[0]
                oversized[1:] = [header + '\n' + chunk for chunk in oversized[1:]]
            chunks += oversized
            chunk_idx += 1
        elif len(split_documents[chunk_idx]) < min_chars and chunk_idx < len(split_documents) - 1:
            idx = chunk_idx + 1
            for item in split_documents[chunk_idx + 1:]:
                if len(split_documents[chunk_idx]) + len(SEPARATOR_TOKEN.join(split_documents[chunk_idx + 1: idx + 1])) < min_chars:
                    idx += 1
                else:
                    chunks.append(split_documents[chunk_idx] + SEPARATOR_TOKEN + SEPARATOR_TOKEN.join(split_documents[chunk_idx + 1: idx + 1]))
                    chunk_idx = idx + 1
                    break
        else:
            chunks.append(split_documents[chunk_idx])
            chunk_idx += 1
    return chunks

def chunk_merged_articles(chunks: list, min_chars: int, max_chars: int, chunk_overlap: int):
    splitter = RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=chunk_overlap)
    chunked_articles = []
    for chunk in chunks:
        articles = chunk.split(SEPARATOR_TOKEN)
        if len(articles[-1]) > max_chars and len(articles) > 1:
            heading = articles[-1].partition("\n")[0]
            split_large_article = splitter.split_text(articles[-1])
            split_large_article[0] = "\n\n".join(articles[:-1]) + "\n\n" + split_large_article[0]
            split_large_article[1:] = [heading + '\n' + article_chunk for article_chunk in split_large_article[1:]]
            if len(split_large_article[-1]) < min_chars:
                split_large_article[-2] = split_large_article[-2] + '\n' + split_large_article[-1]
                split_large_article = split_large_article[:-1]
            chunked_articles += split_large_article
        else:
            joined_articles = "\n\n".join(articles)
            chunked_articles.append(joined_articles)
    return chunked_articles

def prepend_headings(chunks, heading):
    return [heading + '\n' + chunk for chunk in chunks]

def prepare_documents(texts, filenames, minimum_chunk_size=500, maximum_chunk_size=1000, chunk_overlap=150, outlier_chunk_size=100):
    documents = []
    table = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    with open("patterns.json", 'r') as file:
        patterns = json.load(file)
    for i, name in enumerate(filenames):
        chunked_articles = chunk_by_article(texts[i], patterns[name][0], minimum_chunk_size, maximum_chunk_size, chunk_overlap)
        merged_chunks = chunk_merged_articles(chunked_articles, minimum_chunk_size, maximum_chunk_size, chunk_overlap)
        chunks_with_headings = prepend_headings(merged_chunks, patterns[name][1])
        chunk_documents = [Document(page_content=doc, metadata={"source": name}) for doc in chunks_with_headings] 
        documents += chunk_documents
    documents = [doc for doc in documents if len(doc.page_content) >= outlier_chunk_size]
    documents = list({doc.page_content: doc for doc in documents}.values())
    documents = [Document(page_content=doc.page_content.translate(table), metadata=doc.metadata)
    for doc in documents]
    return documents