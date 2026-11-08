from retrieve import retrieve_documents, reword_query
from generate import answer_questions, format_context
def retrieve_and_generate(query, k=5):
    reworded_query = reword_query(query)
    retrieved_documents = retrieve_documents(reworded_query, k)
    context = format_context(retrieved_documents)
    answer = answer_questions(query, context)
    return answer