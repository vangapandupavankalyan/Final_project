import os

import chromadb

from chromadb.config import Settings

from langchain_huggingface import HuggingFaceEmbeddings

DB_PATH = "vector_db"

os.makedirs(DB_PATH, exist_ok=True)


# Local embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Chroma Client
client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="documents"
)


def add_chunks(chunks, metadata):

    embeddings = embedding_model.embed_documents(chunks)

    ids = [
        f"{metadata['filename']}_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        metadata
        for _ in chunks
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )


def search_documents(query, top_k=5):

    query_embedding = embedding_model.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results
def retrieve_context(query, top_k=5):

    results = search_documents(query, top_k)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    context = "\n\n".join(documents)

    sources = []

    for meta in metadatas:
        sources.append(meta["filename"])

    return context, list(set(sources))
def delete_document_embeddings(filename):

    results = collection.get(
        where={"filename": filename}
    )

    if results["ids"]:

        collection.delete(
            ids=results["ids"]
        )