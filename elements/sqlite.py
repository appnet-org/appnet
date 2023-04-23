import sqlite3
from elements import acl, logging, rate_limit


def init_input_table(conn, cursor, print_tables=False):
    # Create the input table
    cursor.execute('''
        CREATE TABLE input (
            user VARCHAR(255),
            message VARCHAR(255)
        )
    ''')

    # Insert data into the input table
    cursor.execute("INSERT INTO input (user, message) VALUES ('Alice', 'Hello World!')")
    cursor.execute("INSERT INTO input (user, message) VALUES ('Bob', 'Hello World!')")
    cursor.execute("INSERT INTO input (user, message) VALUES ('Peter', 'Hello World!')")
    cursor.execute("INSERT INTO input (user, message) VALUES ('Bill', 'Hello World!')")
    cursor.execute("INSERT INTO input (user, message) VALUES ('Jeff', 'Hello World!')")

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

    # Init input table
    init_input_table(conn, cursor, True)

    cursor.execute('''CREATE VIEW acl_input AS
                  SELECT user AS name, message
                  FROM input''')

    # Execute acl elements
    acl(conn, cursor, input_table_name="acl_input", print_tables=True)

    cursor.close()
    conn.close()



