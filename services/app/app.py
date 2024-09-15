import streamlit as st
import time
import uuid
import logging
from assistant import get_answer
from db import save_question, save_user_feedback, get_recent_questions

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_clear(feedback):
    logger.info(f"Feedback received for question '{st.session_state.prev_id}'.")
    save_user_feedback(st.session_state.prev_id, feedback)
    logger.info("Feedback saved to database")
    del st.session_state.prev_id
    st.session_state["input"] = ""
    

def main():
    st.title("'Understanding Deep Learning' Book Assistant")

    # Session state initialization 
    if 'question_id' not in st.session_state:
        st.session_state.question_id = str(uuid.uuid4())
        logger.info(f"New question started with ID: '{st.session_state.question_id}'")
    
    # Create a text area
    user_input = st.text_area("Enter your question:", key="input")

    # Create a button
    if st.button("Ask"):
        if user_input:
            logger.info(f"User asked: '{user_input}'")
            
            with st.spinner("Processing..."):
                logger.info(f"Getting answer from assistant.")
                start_time = time.time()
                answer_data=get_answer(user_input)
                end_time = time.time()
                logger.info(f"Answer received in {end_time - start_time:.2f} seconds")
                st.success("Completed!")
                # Styled output of the answer using custom markdown
                st.markdown(f"""
                <div style="background-color:#f0f0f5; padding: 10px; border-radius: 10px;">
                    <p style="color:#4A90E2;">Answer:</p>
                    <p>{answer_data['answer']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Display monitoring information
                st.markdown(f"""
                <div style="font-size: 14px; margin-top: 10px;">
                    <strong>Model used:</strong> {answer_data['model_used']}<br>
                    <strong>Token Usage:</strong> {answer_data['token_usage']}
                </div>
                """, unsafe_allow_html=True)
                
                # Save conversation to database
                logger.info(f"Saving question to database")
                save_question(st.session_state.question_id, user_input, answer_data)
                logger.info(f"Conversation saved successfully")
                
                # Generate a new conversation ID for next question
                st.session_state.prev_id = st.session_state.question_id
                st.session_state.question_id = str(uuid.uuid4())
        else:
            st.warning("Please enter a question before submitting.")
            logger.warning("Send attempt with empty text")

    # Feedback buttons
    if 'prev_id' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Like", on_click=save_clear, kwargs={'feedback':1}):
                ...
        with col2:
            if st.button("Dislike", on_click=save_clear, kwargs={'feedback':-1}):
                ...

    
    # Display recent questions
    st.subheader("Recent Questions")
    rating_filter = st.selectbox(
        "Filter by rating:", ["All", 1, 2, 3, 4]
    )
    recent_questions = get_recent_questions(limit=5, rating=rating_filter if rating_filter != "All" else None)
    for conv in recent_questions:
        st.markdown(f"""
        <div style="background-color:#f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 10px; border: 1px solid #ddd;">
            <p style="font-size: 18px; color: #333;"><strong>Q:</strong> {conv['question']}</p>
            <p style="font-size: 16px; color: #555; margin-top: 10px;"><strong>A:</strong> {conv['answer']}</p>
            <div style="font-size: 14px; color: #888; margin-top: 10px;">
                <p><strong>Rating:</strong> {conv['rating']}</p>
                <p><strong>Model Used:</strong> {conv['model_used']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
logger.info(f"Streamlit app loop completed")


if __name__ == "__main__":
    logger.info(f"Assistant application started")
    main()