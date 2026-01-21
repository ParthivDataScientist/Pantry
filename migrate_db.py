
import sqlite3

def add_column():
    conn = sqlite3.connect('pantry.db')
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN name_hindi VARCHAR")
        print("Column added successfully")
    except sqlite3.OperationalError as e:
        print(f"Error (probably already exists): {e}")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_column()
