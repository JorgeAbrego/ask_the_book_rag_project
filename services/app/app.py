import streamlit as st
import time
import uuid
import logging
from assistant import get_answer
from db import save_question

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    st.title("'Understanding Deep Learning' Book Assistant")

    # Session state initialization 
    if 'question_id' not in st.session_state:
        st.session_state.question_id = str(uuid.uuid4())
        logger.info(f"New question started with ID: '{st.session_state.question_id}'")
    
    # Create a text area
    user_input = st.text_area("Enter your question:")

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
                st.write(answer_data["answer"])
                
                # Display monitoring information
                st.write(f"Model used: {answer_data['model_used']}")
                st.write(f"Token Usage: {answer_data['token_usage']}")
                
                # Save conversation to database
                logger.info(f"Saving question to database")
                save_question(st.session_state.question_id, user_input, answer_data)
                logger.info(f"Conversation saved successfully")
                # Generate a new conversation ID for next question
                st.session_state.question_id = str(uuid.uuid4())
        else:
            st.warning("Please enter a question before submitting.")
            logger.warning("Send attempt with empty text")

if __name__ == "__main__":
    logger.info(f"Assistant application started")
    main()