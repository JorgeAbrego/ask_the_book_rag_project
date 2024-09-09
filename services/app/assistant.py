import os
import time
import json
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

PG_VECTOR_PWD = os.environ["PG_VECTOR_PWD"]

model_embedding = HuggingFaceEmbeddings(model_name='multi-qa-mpnet-base-dot-v1')

pgvector_conn = f"postgresql+psycopg://vector_user:{PG_VECTOR_PWD}@pgvector:5432/vector_db"
collection_name = "udlbook"

vector_store = PGVector(
    embeddings=model_embedding,
    collection_name=collection_name,
    connection=pgvector_conn,
    use_jsonb=True,
)

retriever = vector_store.as_retriever(search_kwargs={'k': 3})

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

prompt = """You are an expert in the book 'Understanding Deep Learning'. 
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Keep the answer upto 5 lines unless the user asks for more information

Question:
{question}

Context:
{context}

Answer:
"""

prompt_template = ChatPromptTemplate.from_template(prompt)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_answer(query):
    time.sleep(3)
    qa_rag_chain = (
        {
            "context": (retriever
            |
            format_docs),
            "question": RunnablePassthrough()
        }
        |
        prompt_template
        |
        llm
        )
    result = qa_rag_chain.invoke(query)
    return {
        'answer': result.content,
        'model_used': result.response_metadata['model_name'],
        'token_usage': result.response_metadata['token_usage']
    }