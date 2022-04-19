import connection
from psycopg2 import sql
import util
import server
import os
from datetime import datetime


@connection.connection_handler
def get_column_names(cursor, table):
    query = """
    SELECT column_name 
    FROM information_schema.columns
    WHERE table_schema = 'public' AND table_name = {table_name}"""
    cursor.execute(sql.SQL(query).format(table_name=sql.Literal(table)))
    return [elem.get('column_name') for elem in cursor.fetchall()]


@connection.connection_handler
def get_records_by_search(cursor, searched_word, sort_by, order):
    query = util.get_records_by_search(searched_word, sort_by, order)
    cursor.execute(query)
    search_results = cursor.fetchall()
    for row in search_results:
        for match in row:
            if match in ['title', 'message', 'a_message']:
                highlighted = []
                if searched_word.lower() in str(row[match]).lower():
                    words = row[match].split()
                    for word in words:
                        if word.lower() == searched_word.lower():
                            highlighted.append('<mark>'+word+'</mark>')
                        else:
                            highlighted.append(word)
                row[match] = (" ").join(highlighted)
            print(row[match])
    return search_results


@connection.connection_handler
def get_main_page_data(cursor, arguments):
    questions = util.query_select_fields_from_table('question')
    order_by = util.add_order_by_smt_desc_or_args(arguments)
    limit = util.add_limit_to_query(5)
    cursor.execute(questions + order_by + limit)
    recent_questions = cursor.fetchall()
    return {'questions': recent_questions, 'sort_by_fields': get_column_names('question')}


@connection.connection_handler
def get_list_page_data(cursor, arguments: dict):
    questions = util.query_select_fields_from_table('question')
    order_by = util.add_order_by_smt_desc_or_args(arguments)
    cursor.execute(questions + order_by)
    all_question = cursor.fetchall()
    return {'questions': all_question, 'sort_by_fields': get_column_names('question')}


@connection.connection_handler
def get_question_page_data(cursor, question_id, arguments):
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
    order_by = util.add_order_by_smt_desc_or_args(arguments)
    cursor.execute(answers + where + order_by)
    answers = cursor.fetchall()
    answer_ids = tuple([elem['id'] for elem in answers])

    if answer_ids:
        answer_comments = util.query_select_fields_from_table('comment')
        where = util.add_where_to_query('answer_id', 'in', answer_ids)
        cursor.execute(answer_comments + where)
        answer_comments = cursor.fetchall()

    tags = util.query_select_fields_from_table('question_tag', ['tag_id','name'])
    join = util.add_inner_join_to_query('tag', 'tag_id', 'id')
    where = util.add_where_to_query('question_id', '=', question_id)
    cursor.execute(tags + join + where)
    tags = cursor.fetchall()
    return {'question': question,
            'answers': answers,
            'question_comments': question_comments,
            'answer_comments': answer_comments if answer_ids else '',
            'tags': tags,
            'sort_by_fields': get_column_names('answer')}


@connection.connection_handler
def delete_record_by_identifier(cursor, table,  record_id, question_id, identifier):
    query = util.query_delete_from_table_by_identifier(table, record_id, identifier)
    if question_id:
        query += util.add_and_to_query('question_id', '=', question_id)
    print(query.as_string(cursor))
    cursor.execute(query)


@connection.connection_handler
def add_new_record(cursor, record, question_id, answer_id, request):
    form = dict(request.form)
    if form.get('redirect'):
        del form['redirect']
    if answer_id:
        form.update({'answer_id': answer_id})
    elif question_id:
        form.update({'question_id': question_id})
    if record != 'comment':
        if request.files.get('image').filename:
            form.update({'image': request.files.get('image').filename})
            image = request.files['image']
            path = os.path.join(server.app.config['UPLOAD_FOLDER'], image.filename)
            image.save(path)
    query = util.query_insert(record, form.keys(), form.values())
    cursor.execute(query)


@connection.connection_handler
def get_fields_from_table_by_value(cursor, fields, table, key=None, key_value=None, ordered=False):
    query = util.query_select_fields_from_table(table, fields)
    if key:
        query += util.add_where_to_query(key, '=', key_value)
    if ordered:
        query += util.add_order_by_smt_desc_or_args()
    cursor.execute(query)
    return cursor.fetchone()


@connection.connection_handler
def update_record(cursor, table, form):
    key_value_dict = dict(form)
    if key_value_dict.get('redirect'):
        del key_value_dict['redirect']
    if key_value_dict.get('table'):
        del key_value_dict['table']
    query = util.query_update(table, key_value_dict)
    query += util.add_where_to_query('id', '=', key_value_dict['id'])
    cursor.execute(query)


@connection.connection_handler
def get_tag_table(cursor, table):
    query = util.query_select_fields_from_table(table)
    query += util.add_order_by_smt_desc_or_args({'sort_by': 'name', 'order': 'asc'})
    cursor.execute(query)
    return cursor.fetchall()


@connection.connection_handler
def add_tag_to_question(cursor, question_id, form):
    existing_tags = [tag['name'] for tag in get_tag_table('tag', )]
    if form.get('new_tag'):
        if form['new_tag'].lower() not in existing_tags:
            cursor.execute(util.query_insert('tag', 'name', form['new_tag'].lower()))
        for tag in get_tag_table('tag', ):
            if tag['name'] == form.get('new_tag').lower():
                form.update({form['new_tag'].lower(): tag['id']})
    del form['new_tag']
    print(form)
    for tag in form:
        condition = util.query_select_fields_from_table('question_tag', 'question_id')
        condition += util.add_where_to_query('tag_id', '=', form[tag])
        condition += util.add_and_to_query('question_id', '=', question_id)
        cursor.execute(condition)
        if not cursor.fetchall():
            cursor.execute(util.query_insert('question_tag', ['question_id', 'tag_id'], [question_id, form[tag]]))


@connection.connection_handler
def add_new_user(cursor, email, user_name, password):
    print(user_name)
    query = '''
        INSERT INTO public.users (email, user_name, password)
        VALUES ({email}, {user_name}, {password})'''
    cursor.execute(sql.SQL(query).format(
        email=sql.Literal(email),
        user_name=sql.Literal(user_name),
        password=sql.Literal(password)))


@connection.connection_handler
def get_user_by_email(cursor, email):
    query = '''
        SELECT * FROM public.users
        WHERE email = {email}'''
    cursor.execute(sql.SQL(query).format(email=sql.Literal(email)))
    return cursor.fetchone()