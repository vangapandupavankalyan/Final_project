from dotenv import load_dotenv
load_dotenv()

import os
import google.generativeai as genai

from vector_store import retrieve_context

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
)


async def get_agent_response(message, chat_history):

    # Retrieve context from ChromaDB
    context, sources = retrieve_context(message)

    conversation = ""

    for msg in chat_history:

        role = "User" if msg["role"] == "user" else "Assistant"

        conversation += f"{role}: {msg['content']}\n"

    prompt = f"""
You are an Enterprise Document Assistant.

Answer ONLY using the information present in the context.

If the answer is not available in the context, reply:

"I couldn't find that information in the uploaded documents."

Conversation History:

{conversation}

Context:

{context}

Question:

{message}

Provide a professional answer.
"""

    response = model.generate_content(prompt)

    answer = response.text

    if sources:

        answer += "\n\nSources:\n"

        for source in sources:

            answer += f"- {source}\n"

    return answer