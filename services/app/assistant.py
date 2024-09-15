import os
import time
import json
from groq import Groq
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

PG_VECTOR_PWD = os.environ["PG_VECTOR_PWD"]

judge_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

def setup_vector_store(model_name, collection_name):
    model_embedding = HuggingFaceEmbeddings(model_name=model_name)
    pgvector_conn = f"postgresql+psycopg://vector_user:{PG_VECTOR_PWD}@pgvector:5432/vector_db"
    vector_store = PGVector(
        embeddings=model_embedding,
        collection_name=collection_name,
        connection=pgvector_conn,
        use_jsonb=True
    )
    return vector_store


def setup_llm(model_name, temperature=0, max_tokens=None, timeout=None, max_retries=2):
    """Setup the language model."""
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries
    )


def create_prompt_template():
    """Create the prompt template for the LLM."""
    prompt = """You are an expert in the book 'Understanding Deep Learning'. 
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, just say that you don't know.
    Keep the answer up to 5 lines unless the user asks for more information.

    Question:
    {question}

    Context:
    {context}

    Answer:
    """
    return ChatPromptTemplate.from_template(prompt)


def format_docs(docs):
    """Format documents into a string to provide context."""
    return "\n\n".join(doc.page_content for doc in docs)


def process_query(query, retriever, llm, prompt_template, delay=3):
    """Process the user's query and return the answer."""
    time.sleep(delay)  # Introduce delay for any rate limiting needs
    
    # Chain to process query: Retrieval, formatting, and running prompt template
    qa_rag_chain = (
        {
            "context": (retriever | format_docs),
            "question": RunnablePassthrough()
        }
        | prompt_template
        | llm
    )
    
    result = qa_rag_chain.invoke(query)
    
    return {
        'answer': result.content,
        'model_used': result.response_metadata['model_name'],
        'token_usage': result.response_metadata['token_usage']
    }


def judge_llm(prompt):
    start_time = time.time()
    response = judge_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ])
    answer = response.choices[0].message.content
    tokens = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }
    end_time = time.time()
    response_time = end_time - start_time
    return answer, tokens, response_time


def evaluate_response(question, answer):
    prompt_template = """
    You will be given a user_question and system_answer couple.
    Your task is to provide a 'total rating' scoring how well the system_answer answers the user concerns expressed in the user_question.
    Give your answer on a scale of 1 to 4, where 1 means that the system_answer is not helpful at all, and 4 means that the system_answer completely and helpfully addresses the user_question.

    Here is the scale you should use to build your answer:
    1: The system_answer is terrible: completely irrelevant to the question asked, or very partial
    2: The system_answer is mostly not helpful: misses some key aspects of the question
    3: The system_answer is mostly helpful: provides support, but still could be improved
    4: The system_answer is excellent: relevant, direct, detailed, and addresses all the concerns raised in the question

    Provide your feedback as follows:

    Feedback:::
    Evaluation: (your rationale for the rating, as a text)
    Total rating: (your rating, as a number between 1 and 4)

    You MUST provide values for 'Feedback' and 'Rating' in your answer.

    Now here are the question and answer.

    Question: {question}
    Generated Answer: {answer}

    Please analyze the content and context of the generated answer in relation to the question
    and provide your evaluation in parsable JSON without using code blocks:

    {{
      "Feedback": "[Provide a brief explanation for your evaluation]",
      "Rating": [Provide the evaluation between 1 to 4]
    }}
    """.strip()
    prompt = prompt_template.format(question=question, answer=answer)
    evaluation, tokens, _ = judge_llm(prompt)
    try:
        json_eval = json.loads(evaluation)
        return json_eval['Feedback'], json_eval['Rating'], tokens
    except json.JSONDecodeError:
        return "Failed to parse evaluation", 0, tokens
    

def get_answer(query):
    """Main function to handle the query and provide the final answer."""
    # Setup vector store and LLM
    vector_store = setup_vector_store(
        model_name='multi-qa-mpnet-base-dot-v1', 
        collection_name="udlbook"
    )
    
    retriever = vector_store.as_retriever(search_kwargs={'k': 3})
    
    llm = setup_llm(model_name="llama-3.1-70b-versatile")
    
    # Setup prompt template
    prompt_template = create_prompt_template()
    
    answer_data = process_query(query, retriever, llm, prompt_template)
    
    feedback, rating, tokens_eval = evaluate_response(query, answer_data['answer'])
    
    # Process query
    return {'answer': answer_data['answer'],
            'model_used': answer_data['model_used'], 
            'token_usage': answer_data['token_usage'],
            'feedback': feedback, 
            'rating': rating, 
            'tokens_eval': tokens_eval
           }
