import psycopg2
import connection
from psycopg2 import sql
import util


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
def get_column_names(cursor, table):
    query = """
    SELECT column_name 
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = {table_name}"""
    cursor.execute(sql.SQL(query).format(table_name=sql.Literal(table)))
    return [elem.get('column_name') for elem in cursor.fetchall()]


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
def update_vote_number(cursor, table, id_, vote):
    if vote == 'vote-up':
        vote = '+'
    else:
        vote = '-'
    query = f"""
        UPDATE {table}
        SET vote_number = vote_number {vote} 1
        WHERE id = {id_}"""
    cursor.execute(sql.SQL(query).format(
        table=sql.Identifier(table),
        vote=sql.Literal(vote),
        id_=sql.Literal(id_)))


@connection.connection_handler
def update_message(cursor, table_, id_, message, edited_count=None):
    query = """
        UPDATE {table_}
        SET message = {message},
            {edit_count}
            submission_time = now()::timestamp(0)
        WHERE id = {id_}"""
    if edited_count:
        edit_count = sql.SQL('{edited_count_column} = {edited_count} + 1,').format(
                edited_count_column=sql.Identifier('edited_count'),
                edited_count=sql.Literal(edited_count))
    else:
        edit_count = sql.SQL('')
    cursor.execute(sql.SQL(query).format(
        message=sql.Literal(message),
        id_=sql.Literal(id_),
        table_=sql.Identifier(table_),
        edit_count=edit_count))


@connection.connection_handler
def get_table(cursor, table, columns=None, sort_by=None, order=None, limit=None, selector=None, selected_value=None):
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
    cursor.execute(executable_query)
    return cursor.fetchall()


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
        where message ilike '%{word}%') as a on q.id=a.question_id
        where title ilike '%{word}%'
        or q.message ilike '%{word}%'
        or a.message ilike '%{word}%'
    """
    if sort_by:
        order = 'asc' if order.lower() == 'asc' else 'desc'
        null_handler = "nulls first" if order == "asc" else "nulls last"
        query += """ order by {sort_by} {order} {null_handler}""".format(sort_by=sort_by,
                                                                         order=order,
                                                                         null_handler=null_handler)
    cursor.execute(sql.SQL(query).format(word=sql.SQL(word)))
    return cursor.fetchall()


@connection.connection_handler
def delete_comment_by_comment_id(cursor, comment_id):
    query = '''
    DELETE from comment
    WHERE id = %(comment_id)s
    '''
    cursor.execute(query, {"comment_id": comment_id})




# REFACTOR STARTS HERE

@connection.connection_handler
def get_main_page_data(cursor):
    questions = util.query_select_fields_from_table('question')
    order_by = util.add_order_by_to_query('submission_time')
    limit = util.add_limit_to_query(5)
    cursor.execute(questions + order_by + limit)
    recent_questions = cursor.fetchall()
    return {'questions': recent_questions, 'columns': get_column_names('question')}


@connection.connection_handler
def get_list_page_data(cursor, arguments: dict):
    questions = util.query_select_fields_from_table('question')
    if arguments.get('order'):
        reverse = True if arguments.get('order').lower() == 'desc' else False
        order_by = util.add_order_by_to_query(arguments.get('sort_by'), reverse)
    else:
        # default no reverse arg, False because test purposes
        order_by = util.add_order_by_to_query('submission_time', reverse=False)
    cursor.execute(questions + order_by)
    all_question = cursor.fetchall()
    return {'questions': all_question, 'columns': get_column_names('question')}


@connection.connection_handler
def get_question_page_data(cursor, question_id):
    question = util.query_select_fields_from_table('question')
    where = util.add_where_to_query('id', '=', question_id)
    cursor.execute(question + where)
    question = cursor.fetchall()

    question_comments = util.query_select_fields_from_table('comment')
    where = util.add_where_to_query('question_id', '=', question_id)
    cursor.execute(question_comments + where)
    question_comments = cursor.fetchall()

    answers = util.query_select_fields_from_table('answer')
    where = util.add_where_to_query('question_id', '=', question_id)
    cursor.execute(answers + where)
    answers = cursor.fetchall()
    answer_ids = tuple([elem['id'] for elem in answers])

    if answer_ids:
        answer_comments = util.query_select_fields_from_table('comment')
        where = util.add_where_to_query('answer_id', 'in', answer_ids)
        cursor.execute(answer_comments + where)
        answer_comments = cursor.fetchall()

    tags = util.query_select_fields_from_table('question_tag', 'name')
    join = util.add_inner_join_to_query('tag', 'tag_id', 'id')
    where = util.add_where_to_query('question_id', '=', question_id)
    cursor.execute(tags + join + where)
    tags = [tag['name'] for tag in cursor.fetchall()]
    return {'question': question,
            'answers': answers,
            'question_comments': question_comments,
            'answer_comments': answer_comments if answer_ids else '',
            'tags': tags}
    #comments4question,answers,comment4answers


@connection.connection_handler
def delete_record_by_id(cursor, table, value):
    query = util.query_delete_from_table_by_id(table, value)
    cursor.execute(query)
