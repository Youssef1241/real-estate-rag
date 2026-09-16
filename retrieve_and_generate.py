from retrieve import retrieve_documents
from generate import answer_questions, format_context
def retrieve_and_generate(query, k=5):
    retrieved_documents = retrieve_documents(query, k)
    context = format_context(retrieved_documents)
    answer = answer_questions(query, context)
    return answer