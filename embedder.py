# embedder.py
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from db_config import get_all_metadata
from dotenv import load_dotenv

load_dotenv()

# Output folder for index
INDEX_DIR = "faiss_index"

# Load embedding model
embedding = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))


def flatten_metadata(metadata_dict):
    documents = []
    for db_name, tables in metadata_dict.items():
        for table_name, columns in tables.items():
            if table_name == "__error__":
                continue
            table_desc = f"[{db_name}].[{table_name}] has columns: {', '.join(columns)}"
            documents.append(Document(page_content=table_desc))
    return documents


def build_vector_index():
    metadata = get_all_metadata()
    docs = flatten_metadata(metadata)
    vectorstore = FAISS.from_documents(docs, embedding)
    vectorstore.save_local(INDEX_DIR)
    print(f"✅ Vector index saved to '{INDEX_DIR}' with {len(docs)} entries.")
