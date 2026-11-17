from langchain_qwq import ChatQwen

def make_llm_client() -> ChatQwen:
    return ChatQwen(
    model="qwen3.8-flash",
    max_tokens=3_000,
    timeout=None,
    max_retries=2)
