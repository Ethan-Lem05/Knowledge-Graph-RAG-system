import sqlite3

def create_db():
    """
    Creates a SQLite database and a table named 'kg' if it doesn't already exist.
    The 'kg' table has the following columns:
    - id: VARCHAR(32), primary key
    - text: TEXT, not null
    - embedding: BLOB, not null
    - edges: TEXT, not null
    """
    # Create a connection to the database
    conn = sqlite3.connect('kg.db')

    cursor = conn.cursor()

    #execute the queries

    create_table_query = """
        CREATE TABLE IF NOT EXISTS kg(
            id VARCHAR(32) PRIMARY KEY,
            text TEXT NOT NULL,
            embedding BLOB NOT NULL,
            edges TEXT NOT NULL
        );
        """

    cursor.execute(create_table_query)
    conn.commit()

    #close resoureces
    cursor.close()
    conn.close()

def print_all_rows():
    """
    Prints all rows from the 'kg' table in the 'kg.db' database.
    Raises:
        sqlite3.OperationalError: If there is an error executing the SQL query.
    """
    try:
        conn = sqlite3.connect('kg.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM kg")
        rows = cursor.fetchall()

        for row in rows:
            print(row)

        cursor.close()
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")

def main():
    print_all_rows()
    pass

if __name__ == "__main__":
    main()

