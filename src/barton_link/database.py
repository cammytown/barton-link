import os
import sqlite3

class Database:
    database_path: str = 'barton.db'

    conn: sqlite3.Connection
    c: sqlite3.Cursor

    def connect_to_database(self):
        # Check if the database exists
        if not os.path.exists(self.database_path):
            print("Database does not exist. Creating database...")
            self.initialize_database()

        # Connect to the database
        self.conn = sqlite3.connect(self.database_path)
        self.c = self.conn.cursor()

    def initialize_database(self):
        # Double check that the database does not exist
        #@REVISIT
        if os.path.exists(self.database_path):
            print("ERROR: Database already exists.")
            return

        # Create the database (implicit with connect())
        self.conn = sqlite3.connect(self.database_path)
        self.c = self.conn.cursor()

        # Create config table
        self.c.execute("""CREATE TABLE barton_config (
            id integer PRIMARY KEY,
            name text NOT NULL,
            value text NOT NULL
        )""")

        # Create dialogue excerpt table
        self.c.execute("""CREATE TABLE excerpts (
            id integer PRIMARY KEY,
            excerpt text NOT NULL,
            tags text,
            character text,
            projects text,
            metadata text
        )""")

        # Create character table
        self.c.execute("""CREATE TABLE characters (
            id integer PRIMARY KEY,
            name text NOT NULL,
            description text NOT NULL,
            projects text NOT NULL,
            tags text NOT NULL
        )""")

        # Create project table
        self.c.execute("""CREATE TABLE projects (
            id integer PRIMARY KEY,
            name text NOT NULL,
            description text NOT NULL,
            tags text NOT NULL
        )""")

        # Create tag table
        self.c.execute("""CREATE TABLE tags (
            id integer PRIMARY KEY,
            name text NOT NULL,
            description text NOT NULL
        )""")

        # Create scanned document table
        self.c.execute("""CREATE TABLE scanned_documents (
            id integer PRIMARY KEY,
            source text NOT NULL,
            document_id text NOT NULL
        )""")

    # def execute(self, query):
    #     return self.c.execute(query)

    def test_database(self):
        res = self.c.execute("SELECT name FROM sqlite_master")
        tables = res.fetchall()
        print(f"Tables: {tables}")

        # # Query the database
        # self.c.execute("SELECT * FROM barton")

        # # Print the results
        # for row in self.c:
        #     print(row)

    def close_database(self):
        # Close the connection
        self.conn.close()
