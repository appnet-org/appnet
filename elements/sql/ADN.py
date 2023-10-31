from elements import *


class ADN:
    def __init__(self, cursor, upstream, downstream, verbose=False):
        self.cursor = cursor
        self.verbose = verbose
        self.upstream = upstream
        self.downstream = downstream
        self.elements = []
        self.constraints = []

    def add_elements(self, elements):
        self.elements = elements

        for element in self.elements:
            element.verbose = self.verbose
            element.cursor = self.cursor
            element.init_state()

    def add_constraints(self, constraints):
        self.constraints = constraints

    def compile(self):
        pass

    def run(self):
        for element in self.elements:
            element.egress_process(input_table_name=element.get_name() + "_input")

    def generate_test_input(self):
        # Create the input table
        self.cursor.execute(
            """
            CREATE TABLE input (
                user VARCHAR(255),
                message VARCHAR(255),
                src VARCHAR(255),
                dst VARCHAR(255)
            )
        """
        )

        # Insert data into the input table
        data = [
            ("Alice", "Hello World!", "Client", "Server"),
            ("Bob", "Hello World!", "Client", "Server"),
            ("Peter", "Hello World!", "Client", "Server"),
            ("Bill", "Hello World!", "Client", "Server"),
            ("Jeff", "Hello World!", "Client", "Server"),
        ]

        self.cursor.executemany(
            "INSERT INTO input (user, message, src, dst) VALUES (?, ?, ?, ?)", data
        )

        if self.verbose:
            print("Printing input table...")
            self.cursor.execute("SELECT * FROM input")
            description = self.cursor.description
            column_names = [col[0] for col in description]

            print(column_names)
            rows = self.cursor.fetchall()

            # Print the retrieved data
            for row in rows:
                print(row)
