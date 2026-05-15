import os

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import (
    HuggingFaceEmbeddings
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_core.documents import Document

# =========================================================
# CONFIG
# =========================================================

FAISS_DIR = "vector_db"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# =========================================================
# EMBEDDINGS
# =========================================================

def get_embedding():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"}
    )

# =========================================================
# BUILD VECTOR STORE
# =========================================================

def build_vector_store(transcript: str):

    print("✅ Building FAISS vector store")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_text(transcript)

    docs = [

        Document(
            page_content=chunk,
            metadata={
                "chunk_index": i
            }
        )

        for i, chunk in enumerate(chunks)
    ]

    embeddings = get_embedding()

    # =====================================================
    # CREATE FAISS STORE
    # =====================================================

    vector_store = FAISS.from_documents(
        documents=docs,
        embedding=embeddings
    )

    # =====================================================
    # SAVE LOCALLY
    # =====================================================

    os.makedirs(
        FAISS_DIR,
        exist_ok=True
    )

    vector_store.save_local(
        FAISS_DIR
    )

    print("✅ FAISS vector store saved")

    return vector_store

# =========================================================
# LOAD VECTOR STORE
# =========================================================

def load_vector_store():

    embeddings = get_embedding()

    vector_store = FAISS.load_local(
        FAISS_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("✅ FAISS vector store loaded")

    return vector_store

# =========================================================
# RETRIEVER
# =========================================================

def get_retriever(
    vector_store,
    k: int = 4
):

    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k}
    )