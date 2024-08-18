import sqlite3

def create_db():
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
    conn = sqlite3.connect('kg.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM kg")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    conn.close()

def main():
    pass

if __name__ == "__main__":
    main()

