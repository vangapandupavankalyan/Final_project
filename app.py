# this is the changed version of the code
import os
import gradio as gr
from vector_store import delete_document_embeddings
from document_processor import delete_uploaded_file

from agent import get_agent_response
from database import *
from document_processor import save_document, process_document
from vector_store import add_chunks

with open("styles.css", "r") as f:
    CUSTOM_CSS = f.read()

# ---------------- Initialize Database ----------------

init_db()


# ---------------- Upload Function ----------------

def upload_documents(files):

    if not files:

        docs = get_documents()

        return gr.update(
            choices=docs,
            value=None
        )

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

    with gr.Blocks(
        title="🧠 Enterprise Knowledge Workspace",
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS
    ) as demo:

        # ================= HEADER =================

        gr.HTML("""
<div style="
    background: linear-gradient(90deg,#0f172a,#1e293b);
    padding:25px;
    border-radius:15px;
    color:white;
    margin-bottom:15px;
">

<h1 style="margin:0;">
🧠 Enterprise Knowledge Workspace
</h1>

<p style="margin-top:10px;font-size:18px;color:#cbd5e1;">
AI Powered Enterprise Document Assistant
</p>

</div>
""")
        with gr.Row():

            with gr.Column():

                gr.HTML("""

                <div style="
                padding:20px;
                background:#2563eb;
                border-radius:18px;
                color:white;
                text-align:center;
                ">

                <h2>📄</h2>

                <h3>Documents</h3>

                Connected

                </div>

                """)

            with gr.Column():

                gr.HTML("""

                <div style="
                padding:20px;
                background:#059669;
                border-radius:18px;
                color:white;
                text-align:center;
                ">

                <h2>🗄</h2>

                <h3>Vector Store</h3>

                ChromaDB

                </div>

                """)

            with gr.Column():

                gr.HTML("""

                <div style="
                padding:20px;
                background:#9333ea;
                border-radius:18px;
                color:white;
                text-align:center;
                ">

                <h2>🤖</h2>

                <h3>Gemini</h3>

                Connected

                </div>

                """)

            with gr.Column():

                gr.HTML("""

                <div style="
                padding:20px;
                background:#ea580c;
                border-radius:18px;
                color:white;
                text-align:center;
                ">

                <h2>💾</h2>

                <h3>SQLite</h3>

                Ready

                </div>

                """)

        # ================= MAIN LAYOUT =================

        with gr.Row():

            # ============================================================
            # LEFT SIDEBAR
            # ============================================================

            with gr.Column(scale=1, min_width=320):

                gr.Markdown("""
                    # 📂 Document Library

                    Upload, manage and search
                    enterprise documents.
                    """)

                uploaded_docs = gr.Radio(
                    label="Uploaded Documents",
                    choices=get_documents(),
                    interactive=True
                )

                pdf_upload = gr.File(
                    label="Upload PDF Files",
                    file_types=[".pdf"],
                    file_count="multiple"
                )

                upload_btn = gr.Button(
                    "📤 Upload Documents",
                    variant="primary"
                )

                delete_btn = gr.Button(
                    "🗑 Delete Selected Document",
                    variant="stop"
                )

            # ============================================================
            # RIGHT PANEL
            # ============================================================

            with gr.Column(scale=3):

                gr.Markdown("""
                # 🤖 Enterprise AI Assistant

                Ask questions across all uploaded documents.
                """)

                history = gr.Chatbot(
                    elem_id="chatbot",
                    type="messages",
                    show_label=False,
                    height=700
                )

                msg = gr.Textbox(
                    placeholder="Ask anything about your uploaded documents...",
                    show_label=False,
                    container=False
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

        # ================= STATUS BAR =================

        gr.Markdown(
            """
---
🟢 **Gemini Connected** &nbsp;&nbsp;&nbsp;
🗄 **ChromaDB Ready** &nbsp;&nbsp;&nbsp;
💾 **SQLite Connected** &nbsp;&nbsp;&nbsp;
⚡ **Local RAG Enabled**
"""
        )

        # ================= BUTTON CALLBACKS =================

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

        # ================= CHAT FUNCTIONS =================

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
        server_name="127.0.0.1",
        server_port=8080,
        share=False,
        inbrowser=True
    )
