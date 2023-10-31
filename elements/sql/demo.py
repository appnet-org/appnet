import sqlite3
import time

from ADN import *

from elements import ACL, Logging, RateLimit

if __name__ == "__main__":
    # conn = sqlite3.connect("demo.db")
    db = sqlite3.connect(":memory:")
    cursor = db.cursor()

    # Init a new connection
    connection = ADN(cursor, upstream="Client", downstream="Server", verbose=True)

    # Init elements
    acl_transform = """CREATE TABLE acl_input AS SELECT user AS name, * FROM input"""
    logging_transform = """CREATE TABLE logging_input AS SELECT * FROM output"""
    rate_limit_transform = """CREATE TABLE rate_limit_input AS SELECT * FROM output"""
    acl = ACL(acl_transform)
    logging = Logging(logging_transform)
    rate_limit = RateLimit(rate_limit_transform, time_unit=1, tokens=1)

    # Add elements
    connection.add_elements([acl, logging, rate_limit])
    # Add constraints (e.g., logging>acl means logging should be ordered before acl)
    connection.add_constraints("rate_limit>logging, logging>acl")

    # Compile the elements
    connection.compile()
    time.sleep(2)

    # Init input table
    connection.generate_test_input()

    # Run elements
    connection.run()

    cursor.close()
    db.close()
