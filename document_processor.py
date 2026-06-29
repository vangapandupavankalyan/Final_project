import os
import shutil
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_document(file):

    file_path = file.name if hasattr(file, "name") else file

    destination = os.path.join(
        UPLOAD_FOLDER,
        os.path.basename(file_path)
    )

    shutil.copy(file_path, destination)

    return destination


def process_document(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    return chunks
def delete_uploaded_file(filename):

    import os

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if os.path.exists(file_path):

        os.remove(file_path)