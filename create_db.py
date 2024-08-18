import sqlite3

def main():
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

if __name__ == "__main__":
    main()

