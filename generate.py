from clients import make_llm_client
from models import Statements
from langchain_core.prompts import SystemMessage, HumanMessage
from prompts import ANSWER_USER_PROMPT, ANSWER_SYSTEM_PROMPT
def answer_questions(query, context):
    model = make_llm_client()
    structured_output_model = model.with_structured_output(schema=Statements)
    human_message = HumanMessage(content=ANSWER_USER_PROMPT.format(context=context, query=query))
    messages = [
        SystemMessage(content=ANSWER_SYSTEM_PROMPT),
        HumanMessage(content=human_message),
    ]
    response = structured_output_model.invoke(messages)
    return response.content

def format_context(documents):
    context = ""
    for doc in documents:
        context += f"ID: {doc.id}\nFilename: {doc.metadata['source']}\n{doc.page_content}\n\n"
    return context