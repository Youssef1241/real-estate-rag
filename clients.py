from langchain_qwq import ChatQwen
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

def make_llm_client() -> ChatQwen:
    return ChatQwen(
    model="qwen3.8-flash",
    max_tokens=3_000,
    timeout=None,
    max_retries=2)

def make_embedding_client() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
    model="qwen3.7-text-embedding", 
    openai_api_base="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    check_embedding_ctx_length=False)

def make_vector_store_client(embeddings: OpenAIEmbeddings) -> Chroma:
    return Chroma(
        collection_name=embeddings.model,
        embedding_function=embeddings,
        persist_directory="./chroma_vector_store",
    )