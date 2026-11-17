import json
import chainlit as cl
from mcp import ClientSession
from helpers import *
from dotenv import load_dotenv
load_dotenv()

MAX_ATTEMPTS = 2


def parse_tool_result(result):
    """MCP call_tool returns a CallToolResult; pull the JSON payload out of it."""
    if getattr(result, "structuredContent", None):
        content = result.structuredContent
    else:
        content = json.loads(result.content[0].text)
    if isinstance(content, dict) and "result" in content:
        return content["result"]
    return content


@cl.on_mcp_connect
async def on_mcp_connect(connection, session: ClientSession):
    cl.user_session.set("mcp_session", session)


@cl.on_message
async def main(message: cl.Message):
    session: ClientSession = cl.user_session.get("mcp_session")

    async with cl.Step(name="Searching documents", type="tool") as step:
        result = await session.call_tool("search_documents", {"query": message.content})
        step.output = "Documents retrieved"
    context = format_context(result)


    for attempt in range(1, MAX_ATTEMPTS + 1):
        msg = cl.Message(content="")
        if attempt > 1:
            msg.content = ""
        await msg.send()

        answers = answer_questions(message.content, context)
        msg.content = " ".join(a.statement for a in answers.statements)
        print("after model1: ",answers)
        await msg.update()
        
        formatted_answers = [{
            "statement": answer.statement,
            "source": answer.source
        } for answer in answers.statements]
        found_answer = formatted_answers and all(
            isinstance(doc["source"], str)
            and len(doc["source"]) == 12
            and all(c in "0123456789abcdef" for c in doc["source"].lower())
            for doc in formatted_answers
        )
        print("Found ansewr: ", found_answer)

        if found_answer:
            async with cl.Step(
                name=f"Verifying citations (attempt {attempt}/{MAX_ATTEMPTS})",
                type="tool",
            ) as verify_step:                   
                    verified = await session.call_tool("verify_citations", {"answers": formatted_answers})
                    verified_items = parse_tool_result(verified)
                    failed = [i for i in verified_items if not i.get("verdict")]
                    print("after verf: ",verified_items)

                    if not failed:
                        verify_step.output = "✅ تم التحقق من كل الاستشهادات"
                    else:
                        verify_step.output = f"❌ فشل التحقق من {len(failed)} جملة"

            if not failed:
                print("entered not failed")
                content, elements = build_cited_answer(answers.statements, result)
                await msg.remove()
                await cl.Message(
                    content=content + "\n\n✅ *تم التحقق من المصادر*",
                    elements=elements
                ).send()
                return

        if attempt < MAX_ATTEMPTS:
            msg.content = "⚠️ *تعذر التحقق من الإجابة من المصادر. سأحاول مرة أخرى…*"
            await msg.update()
        else:
            msg.content = (
                "❌ لم أتمكن من إنتاج إجابة يمكن التحقق منها من المستندات. "
                "حاول إعادة صياغة السؤال أو جعله أكثر تحديدًا."
            )
            await msg.update()