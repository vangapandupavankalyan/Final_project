# this is the changed version of the code
import os
import gradio as gr
from vector_store import delete_document_embeddings
from document_processor import delete_uploaded_file

from agent import get_agent_response
from database import *
from document_processor import save_document, process_document
from vector_store import add_chunks

# ---------------- Initialize Database ----------------

init_db()


# ---------------- Upload Function ----------------

def upload_documents(files):

    if not files:
        return [[doc] for doc in get_documents()]

    for file in files:

        # Save PDF
        saved_path = save_document(file)

        filename = os.path.basename(saved_path)

        # Save filename into SQLite
        add_document(filename)

        # Extract chunks
        chunks = process_document(saved_path)

        # Store chunks in ChromaDB
        add_chunks(
            chunks,
            {
                "filename": filename
            }
        )

    # Return all uploaded documents
    docs = get_documents()

    return gr.update(
        choices=docs,
        value=None
    )


# ---------------- UI ----------------

def create_gradio_interface():

    with gr.Blocks(title="🤖 Enterprise Document Chatbot") as demo:

        gr.Markdown("# 🤖 Enterprise Document Chatbot")

        # ---------------- Upload Section ----------------

        gr.Markdown("## 📂 Upload PDF Documents")

        pdf_upload = gr.File(
            label="Choose PDF Files",
            file_types=[".pdf"],
            file_count="multiple"
        )

        upload_btn = gr.Button(
            "📤 Upload Documents",
            variant="primary"
        )

        uploaded_docs = gr.Radio(
            label="📂 Uploaded Documents",
            choices=get_documents(),
            interactive=True
        )

        delete_btn = gr.Button(
            "🗑 Delete Selected Document",
            variant="stop"
        )

        # ---------------- Button Callbacks ----------------

        upload_btn.click(
            fn=upload_documents,
            inputs=pdf_upload,
            outputs=uploaded_docs
        )

        delete_btn.click(
            fn=remove_document,
            inputs=uploaded_docs,
            outputs=uploaded_docs
        )

        # ---------------- Chatbot ----------------

        history = gr.Chatbot(
            elem_id="chatbot",
            type="messages",
            height=500,
            show_label=False
        )

        msg = gr.Textbox(
            placeholder="Ask questions about your uploaded documents...",
            show_label=False
        )

        with gr.Row():

            submit_btn = gr.Button(
                "Send",
                variant="primary"
            )

            clear_btn = gr.ClearButton(
                [msg, history],
                value="Clear Chat"
            )

        # ---------------- CSS ----------------

        css = """
        #chatbot {
            height:500px;
        }

        .gradio-container{
            max-width:950px;
            margin:auto;
        }
        """

        demo.css = css

        # ---------------- Chat Functions ----------------

        def user_submit(message, history):

            if not message:
                return "", history

            history = history + [
                {
                    "role": "user",
                    "content": message
                }
            ]

            return "", history

        async def call_agent(history):

            if not history:
                return history

            if history[-1]["role"] != "user":
                return history

            user_message = history[-1]["content"]

            chat_history = history[:-1]

            response = await get_agent_response(
                user_message,
                chat_history
            )

            history.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            return history

        submit_btn.click(
            user_submit,
            inputs=[msg, history],
            outputs=[msg, history]
        ).then(
            call_agent,
            inputs=history,
            outputs=history
        )

    return demo
def remove_document(filename):

    if filename:

        delete_uploaded_file(filename)

        delete_document(filename)

        delete_document_embeddings(filename)

    docs = get_documents()

    return gr.update(
        choices=docs,
        value=None
    )

# ---------------- Launch ----------------

if __name__ == "__main__":

    app = create_gradio_interface()

    app.launch(
        server_name="0.0.0.0",
        server_port=8080,
        share=False
    )