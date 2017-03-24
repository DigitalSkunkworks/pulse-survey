import sqlite3

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except:
        pass

    return None

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except:
        pass

    return None

def main():

    database = "survey.db"

    sql_create_details = """     CREATE TABLE "details"
        (
        "ID" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "first_name"     VARCHAR,
        "surname"   	 VARCHAR,
        "id_num"         NUMERIC,
        "role"    		 VARCHAR,
        "team"    		 VARCHAR,
        "department"     VARCHAR,
        "account"        VARCHAR,
        "company"        VARCHAR,
        "comments"       VARCHAR,
        "date_created" DATETIME DEFAULT CURRENT_TIMESTAMP
        ); """

    # create a database connection
    conn = create_connection(database)
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_details)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()

