import os
import psycopg
from psycopg.rows import dict_row
from datetime import datetime
from zoneinfo import ZoneInfo

PG_APP_PWD = os.environ["PG_APP_PWD"]
tz = ZoneInfo("America/La_Paz")

def get_db_connection():
    return psycopg.connect(
        host='postgres',
        user='app_user',
        password=PG_APP_PWD,
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
                (id, question, answer, model_used, 
                prompt_tokens, completion_tokens, total_tokens, 
                response_time,
                rating, feedback, 
                eval_prompt_tokens, eval_completion_tokens, eval_total_tokens, 
                "timestamp")
	            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, COALESCE(%s, CURRENT_TIMESTAMP));
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
                    answer_data["rating"],
                    answer_data["feedback"],
                    answer_data["tokens_eval"]["prompt_tokens"],
                    answer_data["tokens_eval"]["completion_tokens"],
                    answer_data["tokens_eval"]["total_tokens"],
                    timestamp,
                )
            )
        conn.commit()
    finally:
        conn.close()
        

def save_user_feedback(question_id, feedback, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now(tz)

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feedback (question_id, feedback, timestamp) VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP))",
                (question_id, feedback, timestamp),
            )
        conn.commit()
    finally:
        conn.close()
        
        
def get_recent_questions(limit=5, rating=None):
    conn = get_db_connection()
    try:
        with conn.cursor(row_factory=dict_row) as cur:
            query = """
                SELECT r.*, f.feedback
                FROM requests r
                    LEFT JOIN feedback f ON r.id = f.question_id
            """
            if rating:
                query += f" WHERE r.rating = '{rating}'"
            query += " ORDER BY r.timestamp DESC LIMIT %s"
            cur.execute(query, (limit,))
            return cur.fetchall()
    finally:
        conn.close()