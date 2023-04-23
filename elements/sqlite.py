import sqlite3
from elements import ACL, Logging


def init_input_table(conn, cursor, print_tables=False):
    # Create the input table
    cursor.execute('''
        CREATE TABLE input (
            user VARCHAR(255),
            message VARCHAR(255),
            src VARCHAR(255),
            dst VARCHAR(255)
        )
    ''')

    # Insert data into the input table
    data = [
        ('Alice', 'Hello World!', 'Client', 'Server'),
        ('Bob', 'Hello World!', 'Client', 'Server'),
        ('Peter', 'Hello World!', 'Client', 'Server'),
        ('Bill', 'Hello World!', 'Client', 'Server'),
        ('Jeff', 'Hello World!', 'Client', 'Server')
    ]

    cursor.executemany("INSERT INTO input (user, message, src, dst) VALUES (?, ?, ?, ?)", data)

    if print_tables:
        cursor.execute("SELECT * FROM input")
        description = cursor.description
        column_names = [col[0] for col in description]

        print(column_names)
        rows = cursor.fetchall()

        # Print the retrieved data
        for row in rows:
            print(row)

        # Commit the changes
    conn.commit()


if __name__ == "__main__":
    conn = sqlite3.connect("demo.db")

    # Create a cursor
    cursor = conn.cursor()

    # Init elements
    acl = ACL(cursor, verbose=True)
    logging = Logging(cursor, verbose=True)

    # Init input table
    init_input_table(conn, cursor, print_tables=False)

    cursor.execute('''CREATE TABLE acl_input AS
                  SELECT user AS name, *
                  FROM input''')

    # Execute acl elements
    
    acl.process(conn, cursor, input_table_name="acl_input")

    cursor.execute('''CREATE TABLE logging_input AS
                  SELECT * FROM output''')
                
    logging.process(conn, cursor, input_table_name="logging_input")

    # cursor.execute('''CREATE TABLE rate_limit_input AS
    #             SELECT * FROM output''')

    # rate_limit(conn, cursor, init_input_table="rate_limit_input", print_tables=True)

    # cursor.close()
    # conn.close()



