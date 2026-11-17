import json
from langchain_core.messages import SystemMessage, HumanMessage
from clients import make_llm_client
from prompts import ANSWER_SYSTEM_PROMPT, ANSWER_USER_PROMPT
from models import Statements
import chainlit as cl

def format_context(documents):
    context = ""
    for doc in documents.content:
        parsed_doc = json.loads(doc.text)
        context += f"ID: {parsed_doc['chunk_id']}\n{parsed_doc["page_content"]}\n\n"
    return context

def answer_questions(query, context):
    model = make_llm_client()
    structured_output_model = model.with_structured_output(schema=Statements)
    messages = [
        SystemMessage(content=ANSWER_SYSTEM_PROMPT),
        HumanMessage(content=ANSWER_USER_PROMPT.format(context=context, query=query)),
    ]
    response = structured_output_model.invoke(messages)
    return response

def build_cited_answer(statements, documents):
    """Returns (content, elements): statements with source chips + side-panel text."""
    chunks = {}
    for item in documents.content:
        parsed = json.loads(item.text)
        chunks[str(parsed["chunk_id"])] = parsed

    elements = []
    chip_names = {}
    parts = []

    for s in statements:
        chunk_id = str(s.source)
        doc = chunks.get(chunk_id)
        if doc is None:
            parts.append(s.statement)
            continue

        if chunk_id not in chip_names:
            filename = doc.get("source", "").rsplit("/", 1)[-1] or "مصدر"
            chip = f"📄 {filename} ({chunk_id})"
            chip_names[chunk_id] = chip
            elements.append(
                cl.Text(
                    name=chip,
                    content=str(doc["page_content"]),
                    display="side",
                )
            )
        parts.append(f"{s.statement} {chip_names[chunk_id]}")

    return " ".join(parts), elements 