import sqlite3

def main():
    # Create a connection to the database
    conn = sqlite3.connect('kg.db')

    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXIST kg(
        id = VARCHAR(32) PRIMARY_KEY,
        text = TEXT NOT NULL,
        embedding = BLOB NOT NULL
    );
    """

    cursor.execute(create_table_query)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

