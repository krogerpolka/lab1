import csv
from connect import get_connection


def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,  
        name VARCHAR(100),
        phone VARCHAR(20)
    );
    """)
    conn.commit()
    cur.close()
    conn.close()


def insert_from_csv(filename):
    conn = get_connection()
    cur = conn.cursor()
    count = 0

    with open(filename, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                (row[0], row[1])
            )
            count += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f" added {count} contacts from file '{filename}'")


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
    print(f"contact '{name}' — {phone} successfully added")


def update_contact():
    name = input("Enter name to update: ")
    new_name = input("New name: ")
    new_phone = input("New phone: ")

    conn = get_connection()
    cur = conn.cursor()
    updated = False

    if new_name:
        cur.execute("UPDATE phonebook SET name=%s WHERE name=%s", (new_name, name))
        if cur.rowcount > 0:
            print(f"Name changed: '{name}' → '{new_name}'")
            updated = True

    if new_phone:
        target = new_name if new_name else name
        cur.execute("UPDATE phonebook SET phone=%s WHERE name=%s", (new_phone, target))
        if cur.rowcount > 0:
            print(f"Number updated: {new_phone}")
            updated = True

    if not updated:
        print("Contact is not found or nothing changed")

    conn.commit()
    cur.close()
    conn.close()


def query_contacts():
    choice = input("Search by (1-name / 2-phone prefix): ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", ('%' + name + '%',))
    elif choice == "2":
        prefix = input("Enter phone prefix: ")
        cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s", (prefix + '%',))
    else:
        print("Wrong choose")
        cur.close()
        conn.close()
        return

    rows = cur.fetchall()
    if rows:
        print(f"\n Found {len(rows)} contacts:")
        for row in rows:
            print(f"  ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
    else:
        print("Contacts are not found")

    cur.close()
    conn.close()


def delete_contact():
    choice = input("Delete by (1-name / 2-phone): ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("DELETE FROM phonebook WHERE name=%s", (name,))
        deleted = cur.rowcount
        print(f"Deleted {deleted} contact '{name}'" if deleted else f"Contact '{name}' not found")
    elif choice == "2":
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))
        deleted = cur.rowcount
        print(f"Deleted {deleted} contact '{phone}'" if deleted else f"Phone '{phone}' not found")
    else:
        print("wrong choose")

    conn.commit()
    cur.close()
    conn.close()

def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print(" Phonebook is empty")
        return

    print(f"\n{'─'*40}")
    print(f"{'ID':<5} {'Name':<20} {'Phone':<15}")
    print(f"{'─'*40}")
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<15}")
    print(f"{'─'*40}")
    print(f"Total: {len(rows)} contact(s)")


def menu():
    create_table()

    while True:
        print("\n--- PHONEBOOK ---")
        print("1 - Insert from CSV")
        print("2 - Insert from console")
        print("3 - Update contact")
        print("4 - Search")
        print("5 - Delete")
        print("6 - Show all contacts")  
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
        elif choice == "6":
            show_all_contacts()  
        elif choice == "0":
            print("Bye")
            break
        else:
            print("Wrong choose")
if __name__ == "__main__":
    menu()

