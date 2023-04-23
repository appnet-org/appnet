def acl(conn, cursor, input_table_name, print_tables=False):
    print("Executing ACL element...")
    # Create the "acl" table
    cursor.execute('''CREATE TABLE acl (
                    name VARCHAR(255),
                    permission CHAR(2) not null
                )''')

    # Insert data into the "acl" table
    cursor.executemany("INSERT INTO acl (permission, name) VALUES (?, ?)",
                [('Y', 'Alice'), ('N', 'Bob'), ('Y', 'Peter'), ('Y', 'Jeff'), ('Y', 'Bill')])

    if print_tables:
        print("Printing acl table...")
        cursor.execute("SELECT * FROM acl")
        description = cursor.description
        column_names = [col[0] for col in description]

        print(column_names)
        rows = cursor.fetchall()

        # Print the retrieved data
        for row in rows:
            print(row)

    # Create the "output" table based on a query
    # TODO: make name and message arguments
    # Delete the existing table
    cursor.execute('''DROP TABLE IF EXISTS output''')
    cursor.execute('''CREATE TABLE output AS
                    SELECT {}.name, message from {} JOIN acl on {}.name = acl.name
                    WHERE acl.permission = "Y"'''.format(input_table_name, input_table_name, input_table_name))

    if print_tables:
        print("Printing output table...")
        cursor.execute("SELECT * FROM output")
        description = cursor.description
        column_names = [col[0] for col in description]

        print(column_names)
        rows = cursor.fetchall()

        # Print the retrieved data
        for row in rows:
            print(row)

    conn.commit()



def logging(conn, cursor, print_table=False):
    pass

def rate_limit(conn, cursor, print_table=False):
    pass
