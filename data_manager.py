import csv
import os
import connection
from datetime import datetime

QUESTION_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'question.csv'
ANSWER_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'answer.csv'
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_all_entries(file_path, file_header):
    entries = connection.read_csv(file_path, file_header)
    entries.reverse()
    for entry in entries:
        entry["submission_time"] = datetime.fromtimestamp(int(entry["submission_time"])).strftime("%Y-%m-%d, %H:%M:%S")
    return entries


def get_entry_by_id(entry_id, file_path, file_header):
    entries = connection.read_csv(file_path, file_header)
    key = 'id'
    value = entry_id
    entry = next((entry for entry in entries if entry.get(key) == value), None)
    return entry


def delete_entry(entry_id, file_path, file_header):
    entry = get_entry_by_id(entry_id, file_path, file_header)
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter
