import os
import connection
from datetime import datetime

QUESTION_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'question.csv'
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']


def get_all_questions():
    questions = connection.read_csv(QUESTION_FILE_PATH, QUESTION_HEADER)
    questions.reverse()
    for question in questions:
        question["submission_time"] = datetime.fromtimestamp(int(question["submission_time"])).strftime("%Y-%m-%d, %H:%M:%S")
    return questions
