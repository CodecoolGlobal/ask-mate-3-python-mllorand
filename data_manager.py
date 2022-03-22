import csv
import os
import connection
from datetime import datetime

QUESTION_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'question.csv'
ANSWER_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'answer.csv'
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def get_all_entries(file_path, file_header, sort_by=None, order=None):
    entries = connection.read_csv(file_path, file_header)
    if sort_by is not None:
        if sort_by in ["title", "message"]:
            entries = sorted(entries, key=lambda x: x[sort_by], reverse=order)
        else:
            entries = sorted(entries, key=lambda x: int(x[sort_by]), reverse=order)
    else:
        entries.reverse()
    convert_timestamp_to_date(entries)
    return entries


def convert_timestamp_to_date(entries):
    for entry in entries:
        entry["submission_time"] = datetime.fromtimestamp(int(entry["submission_time"]))\
                                                        .strftime("%Y-%m-%d <br> %H:%M:%S")
    return entries



def get_entry_by_id(entry_id, file_path, file_header):
    entries = connection.read_csv(file_path, file_header)
    key = 'id'
    value = entry_id
    entry = next((entry for entry in entries if entry.get(key) == value), None)
    return entry


def delete_entry(file_path, file_header, entry_to_delete):
    entries = connection.read_csv(file_path, file_header)
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=file_header)
        writer.writeheader()
        for entry in entries:
            if entry == entry_to_delete:
                continue
            writer.writerow(entry)
