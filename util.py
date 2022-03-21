import csv
import os

QUESTION_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'question.csv'
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']


def get_all_question():
    try:
        with open(QUESTION_FILE_PATH) as file:
            questions = [question for question in csv.DictReader(file)]
        return questions
    except FileNotFoundError:
        with open(QUESTION_FILE_PATH, "w") as file:
            file.write(",".join(QUESTION_HEADER))
            file.write("\n")
        return get_all_question()
