import csv
import os
import connection
import util

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
    util.convert_timestamp_to_date(entries)
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


def get_unique_id(file_path, header):
    entries = connection.read_csv(file_path, header)
    try:
        last_story = entries[-1]
        return str(int(last_story["id"])+1)
    except IndexError:
        return 1


if __name__ == "__main__":
    print(get_unique_id(ANSWER_FILE_PATH, ANSWER_HEADER))


def add_new_entry(file_path, file_header, entry_to_add, upload_path):
    entry_to_add = dict(entry_to_add)
    for header in file_header:
        if header == 'id':
            entry_to_add[header] = get_unique_id(file_path, file_header)
        elif header == 'submission_time':
            entry_to_add[header] = util.generate_timestamp()
        elif header in ['view_number', 'vote_number']:
            entry_to_add[header] = 0
        elif header == 'image':
            entry_to_add[header] = upload_path[1:]
    with open(file_path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=file_header)
        writer.writerow(entry_to_add)
    return entry_to_add


def vote_on_entry(file_path, file_header, vote, entry_id):
    entry = get_entry_by_id(entry_id, file_path, file_header)
    if vote == "vote-up":
        entry["vote_number"] = int(entry["vote_number"])+1
    elif vote == "vote-down":
        entry["vote_number"] = int(entry["vote_number"])-1
    old_entries = connection.read_csv(file_path, file_header)
    new_entries =[]
    for old_entry in old_entries:
        if old_entry["id"] == entry["id"]:
            new_entries.append(entry)
        else:
            new_entries.append(old_entry)
    connection.write_csv(file_path, file_header, new_entries)
