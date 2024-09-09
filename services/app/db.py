import os
import psycopg
from datetime import datetime
from zoneinfo import ZoneInfo

tz = ZoneInfo("America/La_Paz")

def get_db_connection():
    return psycopg.connect(
        host='postgres',
        user='app_user',
        password=os.environ("PG_APP_PWD"),
        dbname='app_db',
    )
    
def save_question(question_id, question, answer_data, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)
    
    conn = get_db_connection()
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO requests
                (id, question, answer, model_used, prompt_tokens, completion_tokens, total_tokens, response_time, "timestamp")
	            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP));
                """,
                (
                    question_id,
                    question,
                    answer_data["answer"],
                    answer_data["model_used"],
                    answer_data["token_usage"]["prompt_tokens"],
                    answer_data["token_usage"]["completion_tokens"],
                    answer_data["token_usage"]["total_tokens"],
                    answer_data["token_usage"]["total_time"],
                    timestamp,
                )
            )
        conn.commit()
    finally:
        conn.close()