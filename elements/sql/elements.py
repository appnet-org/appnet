class Element:
    def __init__(self, name, transform, verbose=False):
        self.name = name
        self.verbose = verbose
        self.transform = transform
        self.cursor = None

    def get_name(self):
        return self.name

    def verbose(self, verbose):
        self.verbose = verbose

    def cursor(self):
        self.cursor = cursor

    def print_table(self, table_name):
        if table_name == "output":
            print("----------------------------------------")
        print(f"Printing {table_name} table...")

        self.cursor.execute("SELECT * FROM {}".format(table_name))
        description = self.cursor.description
        column_names = [col[0] for col in description]

        print(column_names)
        rows = self.cursor.fetchall()

        # Print the retrieved data
        for row in rows:
            print(row)

        if table_name == "output":
            print("----------------------------------------")

    # The following three method to be implemented in concrete elements
    def init_state(self):
        pass

    def ingress_process(self, conn, cursor, input_table_name):
        pass

    def egress_process(self, conn, cursor, input_table_name):
        pass


class ACL(Element):
    def __init__(self, transform, verbose=False):
        super().__init__("acl", transform, verbose)

    def init_state(self):
        # Initialize acl database
        self.cursor.execute(
            """CREATE TABLE acl (
                        name VARCHAR(255),
                        permission CHAR(2) not null
                    )"""
        )

        # Insert data into the "acl" table
        data = [
            ("Y", "Alice"),
            ("N", "Bob"),
            ("Y", "Peter"),
            ("Y", "Jeff"),
            ("Y", "Bill"),
        ]
        self.cursor.executemany(
            "INSERT INTO acl (permission, name) VALUES (?, ?)", data
        )

        if self.verbose:
            self.print_table("acl")

    def egress_process(self, input_table_name):
        print(f"Executing {self.name} element...")

        if self.transform:
            self.cursor.execute(self.transform)

        # Create the "output" table based on a query
        # TODO: make name and message arguments
        # Delete the existing table
        self.cursor.execute("""DROP TABLE IF EXISTS output""")
        self.cursor.execute(
            '''CREATE TABLE output AS
                        SELECT {}.name, message, src, dst from {} JOIN acl on {}.name = acl.name
                        WHERE acl.permission = "Y"'''.format(
                input_table_name, input_table_name, input_table_name
            )
        )

        if self.verbose:
            self.print_table("output")


class Logging(Element):
    def __init__(self, transform, verbose=False):
        super().__init__("logging", transform, verbose)

    def init_state(self):
        # Initialize rpc_events database
        self.cursor.execute(
            """
            CREATE TABLE rpc_events (
                timestamp TIMESTAMP,
                src VARCHAR(50),
                dst VARCHAR(50),
                value VARCHAT(256)
            );
        """
        )
        if self.verbose:
            self.print_table("rpc_events")

    def egress_process(self, input_table_name):
        print(f"Executing {self.name} element...")

        if self.transform:
            self.cursor.execute(self.transform)

        self.cursor.execute(
            """INSERT INTO rpc_events (timestamp, src, dst, value)
            SELECT CURRENT_TIMESTAMP, src, dst, name || " " || message FROM {};""".format(
                input_table_name
            )
        )

        self.cursor.execute("""DROP TABLE IF EXISTS output""")
        self.cursor.execute(
            """CREATE TABLE output AS SELECT * from {}""".format(input_table_name)
        )

        if self.verbose:
            self.print_table("output")
            self.print_table("rpc_events")


class RateLimit(Element):
    def __init__(self, transform, time_unit, tokens, verbose=False):
        super().__init__("rate_limit", transform, verbose)
        self.tokens = tokens
        self.time_unit = time_unit

    def init_state(self):
        # Initialize rate limit database
        self.cursor.execute(
            """
            CREATE TABLE token_bucket (
                last_update TIMESTAMP,
                curr_tokens INTEGER
            )
        """
        )

        self.cursor.execute(
            """
            INSERT INTO token_bucket (last_update, curr_tokens)
            VALUES (CURRENT_TIMESTAMP, ?)
        """,
            (self.tokens,),
        )

        if self.verbose:
            self.print_table("token_bucket")

    def egress_process(self, input_table_name):
        print(f"Executing {self.name} element...")

        if self.transform:
            self.cursor.execute(self.transform)

        # Caculate current tokens and number of rpc to forward
        time_diff, curr_tokens = self.cursor.execute(
            """
            SELECT (julianday(CURRENT_TIMESTAMP) - julianday(last_update)) * 86400.00, curr_tokens
            FROM token_bucket
        """
        ).fetchone()
        rpc_count = self.cursor.execute(
            """
           SELECT COUNT(*) FROM {}
        """.format(
                input_table_name
            )
        ).fetchone()[0]
        new_curr_tokens = (
            curr_tokens + round(time_diff, 0) * self.tokens / self.time_unit
        )
        rpc_forward_count = (
            rpc_count if new_curr_tokens > rpc_count else new_curr_tokens
        )

        # Update token bucket table
        self.cursor.execute(
            """UPDATE token_bucket SET curr_tokens={}, last_update=CURRENT_TIMESTAMP""".format(
                str(new_curr_tokens - rpc_forward_count)
            )
        )
        self.cursor.execute("""DROP TABLE IF EXISTS output""")
        self.cursor.execute(
            """CREATE TABLE output AS SELECT * from {} LIMIT {}""".format(
                input_table_name, rpc_forward_count
            )
        )

        if self.verbose:
            self.print_table("output")
