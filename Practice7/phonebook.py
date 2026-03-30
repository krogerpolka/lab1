import csv
from connect import get_connection


def create_table():
    conn = get_connection() #connection to DB
    cur = conn.cursor() #object for doing SQL
#send a command to DB to do SQL 
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,  
        name VARCHAR(100),
        phone VARCHAR(20)
    );
    """) #id auto increasing

    conn.commit() #save changes
    cur.close()
    conn.close() #close the connection


# insert from csv
def insert_from_csv(filename):
    conn = get_connection()
    cur = conn.cursor() # SQL queries are executed

    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (row[0], row[1])
            ) # %s- substitutions of values

    conn.commit()
    cur.close()
    conn.close()



def insert_from_console():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()


# 🔄 Обновление
def update_contact():
    name = input("Enter name to update: ")
    new_name = input("New name: ")
    new_phone = input("New phone: ")

    conn = get_connection()
    cur = conn.cursor()

    if new_name:
        cur.execute("UPDATE phonebook SET name=%s WHERE name=%s", (new_name, name))
    if new_phone:
        cur.execute("UPDATE phonebook SET phone=%s WHERE name=%s", (new_phone, name))

    conn.commit()
    cur.close()
    conn.close()


# Search
def query_contacts():
    choice = input("Search by (1-name / 2-phone prefix): ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", ('%' + name + '%',)) #I-dont look to register, %-partial match
    elif choice == "2":
        prefix = input("Enter phone prefix: ")
        cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s", (prefix + '%',))

    rows = cur.fetchall() #find all records, used after SELECT
    for row in rows:
        print(row)

    cur.close()
    conn.close()


# Deleting
def delete_contact():
    choice = input("Delete by (1-name / 2-phone): ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("DELETE FROM phonebook WHERE name=%s", (name,))
    elif choice == "2":
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))

    conn.commit()
    cur.close()
    conn.close()


# iNTERFACE
def menu():
    create_table()

    while True:
        print("\n--- PHONEBOOK ---")
        print("1 - Insert from CSV")
        print("2 - Insert from console")
        print("3 - Update contact")
        print("4 - Search")
        print("5 - Delete")
        print("0 - Exit")

        choice = input("Choose: ")

        if choice == "1":
            insert_from_csv("contacts.csv")
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            update_contact()
        elif choice == "4":
            query_contacts()
        elif choice == "5":
            delete_contact()
        elif choice == "0":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()