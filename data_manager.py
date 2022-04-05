import csv
import os
import connection
import util
from psycopg2 import sql


QUESTION_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'question.csv'
ANSWER_FILE_PATH = os.getenv('DATA_FILE_PATH') if 'DATA_FILE_PATH' in os.environ else 'answer.csv'
QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


@connection.connection_handler
def get_all_records(cursor, table_):
    query = """
        SELECT * FROM {table_}"""
    cursor.execute(sql.SQL(query).format(
        table_=sql.Identifier(table_)))
    return cursor.fetchall()


@connection.connection_handler
def get_records_by_id(cursor, table_, id_):
    query = """
        SELECT * FROM {table_}
        WHERE id = {id_}"""
    cursor.execute(sql.SQL(query).format(
        table_=sql.Identifier(table_),
        id_=sql.Identifier(id_)))
    return cursor.fetchall()


@connection.connection_handler
def delete_record_by_id(cursor, table_, id_):
    query = """
        DELETE FROM {table_}
        WHERE id = {id_}"""
    cursor.execute(sql.SQL(query).format(
        table_=sql.Identifier(table_),
        id_=sql.Identifier(id_)))
    return cursor.fetchall()


@connection.connection_handler
def add_new_record(cursor, table_, form):
    form = dict(form)
    columns = sql.SQL(', ').join([sql.Identifier(key) for key in form.keys()])
    values_ = sql.SQL(', ').join([sql.Literal(value) for value in form.values()])
    print(columns)
    query = """
        INSERT INTO {table_} ({columns})
        VALUES ({values_})"""
    cursor.execute(sql.SQL(query).format(
        table_=sql.Identifier(table_),
        columns=columns,
        values_=values_))







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
    for old_entry in old_entries:
        if old_entry["id"] == entry["id"]:
            old_entry["vote_number"] = entry["vote_number"]
    connection.write_csv(file_path, file_header, old_entries)


def add_view_to_entry(entry_id, file_path, file_header):
    updatable_entry = get_entry_by_id(entry_id, file_path, file_header)
    old_entries = connection.read_csv(file_path, file_header)
    for old_entry in old_entries:
        if updatable_entry["id"] == old_entry["id"]:
            old_entry["view_number"] = int(old_entry["view_number"]) + 1
    connection.write_csv(file_path, file_header, old_entries)


@connection.connection_handler
def get_table(cursor, table_name, sort_by=None, order=None, limit=None):
    query = """
    select * from """+table_name
    if sort_by:
        query += """
        order by """+sort_by+""" """+order.upper()
    if limit:
        query += """
        limit """+limit
    cursor.execute(query)
    return cursor.fetchall()
