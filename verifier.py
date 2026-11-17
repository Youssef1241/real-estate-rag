from dotenv import load_dotenv
load_dotenv()
from clients import make_llm_client
from prompts import VERIFIER_PROMPT
from models import Verdicts

def verify_answers(answers, vector_store):
    context = ""
    for answer in answers:
        chunk = lookup_chunk(answer['source'], vector_store)
        if chunk is None:
            return 
        context += f"المقطع:\n{chunk.page_content}\n"
        context += f"الجملة:\n{answer['statement']}\n\n"
    verdicts = llm_verify(context)
    return verdicts
        
def llm_verify(context):
    llm = make_llm_client()
    struct_llm = llm.with_structured_output(Verdicts)
    prompt = VERIFIER_PROMPT.format(context = context)
    response = struct_llm.invoke(prompt)
    return response


def lookup_chunk(chunk_id, vector_store):
    ids = vector_store.get()['ids']
    documents = vector_store.get_by_ids(ids)
    document = [doc for doc in documents if doc.metadata['chunk_id'] == chunk_id]
    if document:
        return document[0]
    else: 
        return 