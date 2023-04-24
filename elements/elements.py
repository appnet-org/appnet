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

        if self.verbose: self.print_table(cursor, 'acl')

    def process(self, conn, cursor, input_table_name):
        print(f"Executing {self.name} element...")

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

        # Initialize rpc_events database
        cursor.execute('''
            CREATE TABLE rpc_events (
                timestamp TIMESTAMP,
                src VARCHAR(50),
                dst VARCHAR(50),
                value VARCHAT(256)
            );
        ''')    
        if self.verbose: self.print_table(cursor, "rpc_events")

    def process(self, conn, cursor, input_table_name):
        print(f"Executing {self.name} element...")
        
        cursor.execute('''INSERT INTO rpc_events (timestamp, src, dst, value) 
            SELECT CURRENT_TIMESTAMP, src, dst, name || " " || message FROM {};'''.format(input_table_name))

        cursor.execute('''DROP TABLE IF EXISTS output''')
        cursor.execute('''CREATE TABLE output AS SELECT * from {}'''.format(input_table_name))

        if self.verbose: self.print_table(cursor, "output")


class RateLimit(Element):
    def __init__(self, cursor, time_unit, tokens, verbose=False):
        super().__init__("RateLimit", verbose)
        self.tokens = tokens
        self.time_unit = time_unit

        # Initialize rate limit database
        cursor.execute('''
            CREATE TABLE token_bucket (
                last_update TIMESTAMP,
                curr_tokens INTEGER
            )
        ''')

        cursor.execute('''    
            INSERT INTO token_bucket (last_update, curr_tokens)
            VALUES (CURRENT_TIMESTAMP, ?)
        ''', (tokens,))

        if self.verbose: self.print_table(cursor, "token_bucket")


    def process(self, conn, cursor, input_table_name):
        print(f"Executing {self.name} element...")

        # Caculate current tokens and number of rpc to forward
        time_diff, curr_tokens = cursor.execute('''
            SELECT (julianday(CURRENT_TIMESTAMP) - julianday(last_update)) * 86400.00, curr_tokens
            FROM token_bucket
        ''').fetchone() 
        rpc_count = cursor.execute('''
           SELECT COUNT(*) FROM {}
        '''.format(input_table_name)).fetchone()[0]
        new_curr_tokens = curr_tokens + round(time_diff, 0) * self.tokens / self.time_unit
        rpc_forward_count = rpc_count if new_curr_tokens > rpc_count else new_curr_tokens
        
        # Update token bucket table
        cursor.execute('''UPDATE token_bucket SET curr_tokens={}, last_update=CURRENT_TIMESTAMP'''.format(str(new_curr_tokens-rpc_forward_count)))


        cursor.execute('''DROP TABLE IF EXISTS output''')
        cursor.execute('''CREATE TABLE output AS SELECT * from {} LIMIT {}'''.format(input_table_name, rpc_forward_count))

        if self.verbose: self.print_table(cursor, "output")

