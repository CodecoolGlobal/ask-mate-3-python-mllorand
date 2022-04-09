from psycopg2 import sql


def query_select_fields_from_table(table: str, columns: list = False) -> sql.Composed:
    """Returns an executable SQL SELECT statement. At execution, it fetches the data
    from the selected column(s) from a database.

    Parameters:
        table (str): Table name
        columns (list): Column names
    Returns:
        Composed SQL object
        """
    if columns:
        return sql.SQL('select {columns} from {table}').format(table=sql.Identifier(table),
                                                               columns=sql.Identifier(columns))
    return sql.SQL('select * from {table}').format(table=sql.Identifier(table))


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


def add_limit_to_query(limit: int) -> sql.Composable:
    """Returns a composable SQL LIMIT clause with the given value

    Parameters:
        limit (int):
    Returns:
        Composable SQL object
        """
    return sql.SQL("limit {limit} ").format(limit=sql.Literal(limit))
