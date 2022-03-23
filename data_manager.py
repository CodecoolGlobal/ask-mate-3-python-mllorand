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


def get_all_entries_with_unix_timestamp(file_path, file_header):
    return connection.read_csv(file_path, file_header)


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


def add_new_entry(file_path, file_header, entry_to_add):
    entry_to_add = dict(entry_to_add)
    for header in file_header:
        if header == 'id':
            entry_to_add[header] = get_unique_id(file_path, file_header)
        elif header == 'submission_time':
            entry_to_add[header] = util.generate_timestamp()
        elif header in ['view_number', 'vote_number']:
            entry_to_add[header] = 0
        elif header == 'image':
            entry_to_add[header] = 'image'
    with open(file_path, 'a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=file_header)
        writer.writerow(entry_to_add)
    return entry_to_add


def update_entry(file_path, file_header, entry_to_update):
    entries = connection.read_csv(file_path, file_header)
    print(entry_to_update)
    with open(file_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=file_header)
        writer.writeheader()
        for entry in entries:
            if entry['id'] == entry_to_update['id']:
                entry['submission_time'] = entry_to_update['submission_time']
                entry['view_number'] = entry_to_update['view_number']
                entry['vote_number'] = entry_to_update['vote_number']
                entry['title'] = entry_to_update['title']
                entry['message'] = entry_to_update['message']
                entry['image'] = entry_to_update['image']
            writer.writerow(entry)
