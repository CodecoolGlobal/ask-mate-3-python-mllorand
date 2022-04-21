from psycopg2 import sql
import bcrypt


def query_select_fields_from_table(table: str, columns: list = None) -> sql.Composed:
    """Returns an executable SQL SELECT statement. At execution, it fetches the data
    from the selected column(s) from a table.

    Parameters:
        table (str): Table name
        columns (list): Column names
    Returns:
        Composed SQL object
        """
    if columns:
        if type(columns) is str:
            columns = [columns]
        elif type(columns) is not list:
            columns = list(columns)
        return sql.SQL('select {columns} from {table} ').format(table=sql.Identifier(table),
                                                                columns=sql.SQL(', ').join(map(sql.Identifier, columns)))
    return sql.SQL('select * from {table} ').format(table=sql.Identifier(table))


def add_order_by_to_query(columns: list, reverse: bool = True) -> sql.Composable:
    """Returns a composable SQL ORDER BY clause based on given column(s).
    Default order DESC can be modified with reverse

    Parameters:
        columns (list): Column name(s)
        reverse (bool): True for descending, False for ascending
    Returns:
        Composable SQL object
        """
    if type(columns) is str:
        columns = [columns]
    elif type(columns) is not list:
        columns = list(columns)
    if reverse:
        return sql.SQL("order by {columns} desc ").format(columns=sql.SQL(', ')
                                                          .join(map(sql.Identifier, columns)))
    return sql.SQL("order by {columns} asc ").format(columns=sql.SQL(', ')
                                                     .join(map(sql.Identifier, columns)))


def add_order_by_smt_desc_or_args(arguments=None):
    """add 'order by submission_time descending' to a query by default,
    arguments should be in dict format like {'sort_by': '<column_name>','order': '<asc/desc>'}"""
    if arguments:
        reverse = True if arguments.get('order').lower() == 'desc' else False
        order_by = add_order_by_to_query(arguments.get('sort_by'), reverse)
    else:
        order_by = add_order_by_to_query('submission_time', reverse=True)
    return order_by


def add_limit_to_query(limit: int) -> sql.Composable:
    """Returns a composable SQL LIMIT clause with the given value

    Parameters:
        limit (int):
    Returns:
        Composable SQL object
        """
    return sql.SQL("limit {limit} ").format(limit=sql.Literal(limit))


def add_where_to_query(identifier, operator, value):
    return sql.SQL("where {first_operand} {operator} {second_operand} ").format(
        first_operand=sql.Identifier(identifier),
        operator=sql.SQL(operator),
        second_operand=sql.Literal(value)
    )


def add_and_to_query(identifier, operator, value):
    return sql.SQL("and {first_operand} {operator} {second_operand} ").format(
        first_operand=sql.Identifier(identifier),
        operator=sql.SQL(operator),
        second_operand=sql.Literal(value)
    )


def query_delete_from_table_by_identifier(table, value, identifier, operator='='):
    return sql.SQL("delete from {table} ").format(table=sql.Identifier(table)) + \
           add_where_to_query(identifier, operator, value)


def add_inner_join_to_query(table, first_identifier, second_identifier):
    return sql.SQL("inner JOIN {table} ON {first_identifier} = {second_identifier} ")\
        .format(table=sql.Identifier(table),
                first_identifier=sql.Identifier(first_identifier),
                second_identifier=sql.Identifier(second_identifier))


def query_insert(table, columns, values):
    if type(columns) is str:
        columns = [columns]
        values = [values]
    elif type(columns) is not list:
        columns = list(columns)
        values = list(values)
    return sql.SQL("insert into {table}({columns}) values({values}) ").format(
        table=sql.Identifier(table),
        columns=sql.SQL(', ').join(map(sql.Identifier, columns)),
        values=sql.SQL(', ').join(map(sql.Literal, values))
    )


def query_update(table, key_value_dict):
    query = sql.SQL('update {table} set ').format(table=sql.Identifier(table))
    columns = []
    for key in key_value_dict:
        if key != 'id':
            columns.append(sql.SQL('{column} = {value} ').format(column=sql.Identifier(key),
                                                                 value=sql.Literal(key_value_dict[key])))
    return query+sql.SQL(',').join(columns)


def get_records_by_search(word, sort_by=None, order=None):
    query ="""
            select q.id,a.id as a_id,title,
            q.message,a.message as a_message,
            q.view_number,
            q.vote_number,a.vote_number as a_vote_number,
            q.submission_time,a.submission_time as a_submission_time
            from question as q
            left join
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
    return sql.SQL(query).format(word=sql.SQL(word))


# hashing

def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


def get_tag_page_data():
    query = """select name, count(tag_id) from question_tag
               right join tag t on question_tag.tag_id = t.id
               group by name"""
    return sql.SQL(query)


def modify_reputation(value, id):
    query = """UPDATE users 
               SET reputation_level = reputation_level + {value}
               WHERE user_id = {id}"""
    return sql.SQL(query).format(value=sql.Literal(value), id=sql.Literal(id))


def accept_answer(status, answer_id):
    query = '''
        UPDATE answer
        SET accepted = {status}
        WHERE id = {answer_id}'''
    return sql.SQL(query).format(status=sql.Literal(status),
                                 answer_id=sql.Literal(answer_id))
