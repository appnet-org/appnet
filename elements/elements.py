class Element():
    def __init__(self, name, verbose=False):
        self.name = name
        self.verbose = verbose
    
    def get_name(self):
        return self.name

    def verbose(self, verbose):
        self.verbose = verbose

    def print_table(self, cursor, table_name):
        print(f"Printing {table_name} table...")
        cursor.execute("SELECT * FROM {}".format(table_name))
        description = cursor.description
        column_names = [col[0] for col in description]

        print(column_names)
        rows = cursor.fetchall()

        # Print the retrieved data
        for row in rows:
            print(row)
    
    # To be implemented in concrete elements
    def process(self, conn, cursor, input_table_name):
        pass


class ACL(Element):
    def __init__(self, cursor, verbose=False):
        super().__init__("AccessControlList", verbose)

        # Initialize acl database
        cursor.execute('''CREATE TABLE acl (
                        name VARCHAR(255),
                        permission CHAR(2) not null
                    )''')

        # Insert data into the "acl" table
        data = [('Y', 'Alice'), ('N', 'Bob'), ('Y', 'Peter'), ('Y', 'Jeff'), ('Y', 'Bill')]
        cursor.executemany("INSERT INTO acl (permission, name) VALUES (?, ?)", data)

    def process(self, conn, cursor, input_table_name):
        print(f"Executing {self.name} element...")
        # Create the "acl" table


        if self.verbose: self.print_table(cursor, 'acl')

        # Create the "output" table based on a query
        # TODO: make name and message arguments
        # Delete the existing table
        cursor.execute('''DROP TABLE IF EXISTS output''')
        cursor.execute('''CREATE TABLE output AS
                        SELECT {}.name, message, src, dst from {} JOIN acl on {}.name = acl.name
                        WHERE acl.permission = "Y"'''.format(input_table_name, input_table_name, input_table_name))

        if self.verbose: self.print_table(cursor, 'output')

        conn.commit()

class Logging(Element):
    def __init__(self, cursor, verbose=False):
        super().__init__("Logging", verbose)

        # Initialize acl database
        cursor.execute('''
            CREATE TABLE rpc_events (
                timestamp TIMESTAMP,
                src VARCHAR(50),
                dst VARCHAR(50),
                value VARCHAT(256)
            );
        ''')    

    def process(self, conn, cursor, input_table_name):
        print(f"Executing {self.name} element...")
        
        cursor.execute('''INSERT INTO rpc_events (timestamp, src, dst, value) 
            SELECT CURRENT_TIMESTAMP, src, dst, name || " " || message FROM {};'''.format(input_table_name))

        cursor.execute('''DROP TABLE IF EXISTS output''')
        cursor.execute('''CREATE TABLE output AS SELECT * from {}'''.format(input_table_name))

        if self.verbose:
            self.print_table(cursor, "rpc_events")
            self.print_table(cursor, "output")




def rate_limit(conn, cursor, print_table=False):
    pass
