from psycopg2 import sql


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
        if type(columns) is not list:
            columns = [columns]
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
    if type(columns) is not list:
        columns = [columns]
    if reverse:
        return sql.SQL("order by {columns} desc ").format(columns=sql.SQL(', ')
                                                          .join(map(sql.Identifier, columns)))
    return sql.SQL("order by {columns} asc ").format(columns=sql.SQL(', ')
                                                     .join(map(sql.Identifier, columns)))


def add_order_by_smt_desc_or_args(arguments=None):
    if arguments.get('order'):
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
    return sql.SQL("where {first_operand} {operator} {second_operand}").format(
        first_operand=sql.Identifier(identifier),
        operator=sql.SQL(operator),
        second_operand=sql.Literal(value)
    )


def query_delete_from_table_by_id(table, value, identifier="id", operator='='):
    return sql.SQL("delete from {table}").format(table=sql.Identifier(table)) + \
           add_where_to_query(identifier, operator, value)


def add_inner_join_to_query(table, first_identifier, second_identifier):
    return sql.SQL("inner JOIN {table} ON {first_identifier} = {second_identifier}")\
        .format(table=sql.Identifier(table),
                first_identifier=sql.Identifier(first_identifier),
                second_identifier=sql.Identifier(second_identifier))


def update_vote_number(table, record_id, vote):
    return sql.SQL("""UPDATE {table} SET "vote_number" = "vote_number" {vote} WHERE id = {record_id}""").format(
        table=sql.Identifier(table),
        vote=sql.SQL(vote),
        record_id=sql.Literal(record_id))
