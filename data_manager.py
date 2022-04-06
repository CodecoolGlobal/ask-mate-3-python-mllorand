import datetime

import connection
from psycopg2 import sql


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


def QUESTION_FILE_PATH():
    return None