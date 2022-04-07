import datetime

import psycopg2

import connection
from psycopg2 import sql
import json


@connection.connection_handler
def delete_record_by_id(cursor, table_, selector, selected_value):
    query = """
        DELETE FROM {table_}
        WHERE {selector} = {selected_value}"""
    cursor.execute(sql.SQL(query).format(
        table_=sql.Identifier(table_),
        selector=sql.Identifier(selector),
        selected_value=sql.Literal(selected_value)))


@connection.connection_handler
def add_new_record(cursor, table_, form):
    form = dict(form)
    columns = sql.SQL(', ').join([sql.Identifier(key) for key in form.keys()])
    values_ = sql.SQL(', ').join([sql.Literal(value) for value in form.values()])
    query = """
        INSERT INTO {table_} ({columns})
        VALUES ({values_})"""
    cursor.execute(sql.SQL(query).format(
        table_=sql.Identifier(table_),
        columns=columns,
        values_=values_))


@connection.connection_handler
def get_column_names(cursor, table_):
    query = """
        SELECT *
        FROM {table_}
        LIMIT 0"""
    cursor.execute(sql.SQL(query).format(
        table_=sql.Identifier(table_)))
    return [desc[0] for desc in cursor.description]


@connection.connection_handler
def update_question(cursor, form):
    form = dict(form)
    id_ = sql.Literal(form.get('id'))
    title = sql.Literal(form.get('title'))
    message = sql.Literal(form.get('message'))
    query = """
        UPDATE question
        SET title = {title},
            message = {message}
        WHERE id = {id_}"""
    cursor.execute(sql.SQL(query).format(
        title=title,
        message=message,
        id_=id_))


@connection.connection_handler
def get_table(cursor, table, columns=None, sort_by=None, order=None, limit=None, selector=None, selected_value=None):
    query = query_builder_select(table, columns, sort_by, order, limit, selector, selected_value)
    cursor.execute(query)
    return cursor.fetchall()


def query_builder_select(table, columns: list, sort_by, order, limit, selector, selected_value):
    base_query = """select {columns} from {table}""" if columns else """select * from {table}"""
    if columns:
        executable_query = sql.SQL(base_query).format(table=sql.Identifier(table),
                                                      columns=sql.SQL(', ').join(map(sql.Identifier, columns)))
    else:
        executable_query = sql.SQL(base_query).format(table=sql.Identifier(table))
    if selector and selected_value:
        executable_query += sql.SQL(f""" WHERE {selector} = {selected_value}""").format(
            selector=sql.Identifier(selector),
            selected_value=sql.Literal(selected_value))
    if sort_by:
        order = 'asc' if order.lower() == 'asc' else 'desc'
        executable_query += sql.SQL(""" order by {sort_by} {order}""").format(sort_by=sql.Identifier(sort_by),
                                                                              order=sql.SQL(order))
    if limit:
        executable_query += sql.SQL(""" limit {limit}""").format(limit=sql.Literal(limit))
    return executable_query


@connection.connection_handler
def tag_table(cursor, question_id):
    query = """
        SELECT *
        FROM question_tag t1
        JOIN tag t2
        ON t1.tag_id = t2.id
        WHERE question_id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@connection.connection_handler
def get_tag_by_id(cursor):
    dict_cur = cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute("SELECT id FROM tag")
    rec = dict_cur.fetchone()
    return rec


@connection.connection_handler
def tag_to_question_tag(cursor, question_id, tag_id):
    for cell in tag_id:
        tag_ids = cell.get('id')
    query = f"""
        INSERT INTO question_tag
        VALUES ('{question_id}', '{tag_ids}')"""
    cursor.execute(query)


@connection.connection_handler
def add_existing_tag_to_question_tag(cursor, question_id, tag_id):
    for tag in tag_id:
        query = f"""
            INSERT INTO question_tag
            VALUES ('{question_id}', '{tag}')"""
        cursor.execute(query)


@connection.connection_handler
def get_records_by_search(cursor, word, sort_by=None, order=None):
    query ="""
        select q.id,a.id as a_id,title,
        q.message,a.message as a_message,
        q.view_number,
        q.vote_number,a.vote_number as a_vote_number,
        q.submission_time,a.submission_time as a_submission_time
        from question as q
        full outer join
        (select id,question_id,message,vote_number,submission_time from answer
        where message like '%{word}%') as a on q.id=a.question_id
        where title like '%{word}%'
        or q.message like '%{word}%'
        or a.message like '%{word}%'
    """
    if sort_by:
        order = 'asc' if order.lower() == 'asc' else 'desc'
        null_handler = "nulls first" if order == "asc" else "nulls last"
        query += """ order by {sort_by} {order} {null_handler}""".format(sort_by=sort_by,
                                                                         order=order,
                                                                         null_handler=null_handler)
    cursor.execute(sql.SQL(query).format(word=sql.SQL(word)))
    return cursor.fetchall()


def QUESTION_FILE_PATH():
    return None
