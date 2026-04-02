import csv
from connect import get_connection


def create_table():
    conn = get_connection()       # establish connection to PostgreSQL database
    cur = conn.cursor()           # create cursor object to execute SQL queries
    cur.execute("""
    CREATE TABLE IF NOT EXISTS phonebook (   -- create table only if it doesn't exist yet
        id SERIAL PRIMARY KEY,               -- auto-incrementing unique identifier
        name VARCHAR(100),                   -- contact name, max 100 characters
        phone VARCHAR(20)                    -- phone number, max 20 characters
    );
    """)
    conn.commit()    # save changes to database
    cur.close()      # close cursor
    conn.close()     # close database connection


# --- BASIC INSERT ---

def insert_from_csv(filename):
    conn = get_connection()
    cur = conn.cursor()
    count = 0   # counter for added contacts

    with open(filename, "r") as f:   # open CSV file in read mode
        reader = csv.reader(f)        # create CSV reader object
        for row in reader:            # iterate through each row in file
            cur.execute(
                "SELECT COUNT(*) FROM phonebook WHERE name=%s AND phone=%s",
                (row[0], row[1])      # row[0] = name, row[1] = phone
            )
            exists = cur.fetchone()[0]   # get count result (0 or 1)

            if not exists:               # only insert if contact doesn't exist
                cur.execute(
                    "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
                    (row[0], row[1])     # %s prevents SQL injection
                )
                count += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"Added {count} new contacts from file '{filename}'")
    print("Skipped duplicates")


def insert_from_console():
    name = input("Enter name: ")    # get name from user input
    phone = input("Enter phone: ")  # get phone from user input

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO phonebook (name, phone) VALUES (%s, %s)",
        (name, phone)    # safely pass values using parameterized query
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Contact '{name}' — {phone} successfully added")


# --- ADVANCED INSERT / UPDATE ---

def insert_or_update():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL insert_or_update_user(%s, %s)", (name, phone))  # call stored procedure from procedures.sql
    conn.commit()                                                       # if name exists -> update phone, else -> insert new
    cur.close()
    conn.close()
    print(f"Contact '{name}' — {phone} inserted or updated")


def insert_many_users():
    names = input("Enter names separated by comma: ").split(",")   # split string into list by comma
    phones = input("Enter phones separated by comma: ").split(",")

    if len(names) != len(phones):    # validate that counts match before inserting
        print("Number of names and phones must match")
        return

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL insert_many_users(%s, %s)", (names, phones))  # pass lists directly to PostgreSQL procedure
    conn.commit()
    cur.close()
    conn.close()
    print(f"Added {len(names)} contacts")


# --- UPDATE ---

def update_contact():
    name = input("Enter name to update: ")
    new_name = input("New name (leave empty to skip): ")    # empty input = skip this field
    new_phone = input("New phone (leave empty to skip): ")

    conn = get_connection()
    cur = conn.cursor()
    updated = False    # flag to track if any update happened

    if new_name:    # only update name if user provided a new one
        cur.execute("UPDATE phonebook SET name=%s WHERE name=%s", (new_name, name))
        if cur.rowcount > 0:    # rowcount = number of affected rows (0 means not found)
            print(f"Name changed: '{name}' -> '{new_name}'")
            updated = True

    if new_phone:
        target = new_name if new_name else name    # use new name if it was changed
        cur.execute("UPDATE phonebook SET phone=%s WHERE name=%s", (new_phone, target))
        if cur.rowcount > 0:
            print(f"Phone updated: {new_phone}")
            updated = True

    if not updated:
        print("Contact not found or nothing changed")

    conn.commit()
    cur.close()
    conn.close()


# --- SEARCH ---

def query_contacts():
    choice = input("Search by (1-name / 2-phone prefix): ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("SELECT * FROM phonebook WHERE name ILIKE %s", ('%' + name + '%',))
        # ILIKE = case-insensitive search, % = wildcard (matches any characters)
    elif choice == "2":
        prefix = input("Enter phone prefix: ")
        cur.execute("SELECT * FROM phonebook WHERE phone LIKE %s", (prefix + '%',))
        # prefix% = starts with this prefix
    else:
        print("Wrong choice")
        cur.close()
        conn.close()
        return

    rows = cur.fetchall()    # fetch all matching records from database
    if rows:
        print(f"\nFound {len(rows)} contact(s):")
        for row in rows:
            print(f"  ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
    else:
        print("Contacts not found")

    cur.close()
    conn.close()


def search_pattern():
    pattern = input("Enter pattern (name or phone): ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_phonebook(%s)", (pattern,))   # call function from functions.sql
    rows = cur.fetchall()                                            # searches both name and phone at once

    if rows:
        print(f"\nFound {len(rows)} contact(s):")
        for row in rows:
            print(f"  ID: {row[0]} | Name: {row[1]} | Phone: {row[2]}")
    else:
        print("No contacts found for pattern")

    cur.close()
    conn.close()


# --- DELETE ---

def delete_contact():
    choice = input("Delete by (1-name / 2-phone): ")

    conn = get_connection()
    cur = conn.cursor()

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("DELETE FROM phonebook WHERE name=%s", (name,))
        deleted = cur.rowcount    # number of deleted rows
        print(f"Deleted {deleted} contact(s) '{name}'" if deleted else f"Contact '{name}' not found")
    elif choice == "2":
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))
        deleted = cur.rowcount
        print(f"Deleted {deleted} contact(s) '{phone}'" if deleted else f"Phone '{phone}' not found")
    else:
        print("Wrong choice")

    conn.commit()
    cur.close()
    conn.close()


def delete_user():
    value = input("Enter name or phone to delete: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL delete_user(%s)", (value,))    # stored procedure handles both name and phone deletion
    conn.commit()
    cur.close()
    conn.close()
    print(f"Contact '{value}' deleted")


# --- SHOW / PAGINATION ---

def show_all_contacts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook ORDER BY id")    # fetch all contacts sorted by id
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("Phonebook is empty")
        return

    # format output as a table with fixed column widths
    print(f"\n{'─'*40}")
    print(f"{'ID':<5} {'Name':<20} {'Phone':<15}")    # :<5 = left-align with width 5
    print(f"{'─'*40}")
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<20} {row[2]:<15}")
    print(f"{'─'*40}")
    print(f"Total: {len(rows)} contact(s)")


def pagination():
    limit = int(input("Enter LIMIT: "))     # how many contacts to show per page
    offset = int(input("Enter OFFSET: "))   # how many contacts to skip (page * limit)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_phonebook_page(%s, %s)", (limit, offset))
    # example: limit=5, offset=0 -> first 5 contacts
    # example: limit=5, offset=5 -> next 5 contacts (page 2)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if rows:
        print(f"\nPage (limit={limit}, offset={offset}):")
        print(f"\n{'─'*40}")
        print(f"{'ID':<5} {'Name':<20} {'Phone':<15}")
        print(f"{'─'*40}")
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<15}")
        print(f"{'─'*40}")
    else:
        print("No contacts on this page")


# --- MENU ---

def menu():
    create_table()    # ensure table exists before any operations

    while True:       # keep menu running until user chooses exit
        print("\n--- PHONEBOOK ---")
        print("1  - Insert from CSV")
        print("2  - Insert from console")
        print("3  - Insert or update (procedure)")
        print("4  - Insert many users (procedure)")
        print("5  - Update contact")
        print("6  - Search (name / phone prefix)")
        print("7  - Search by pattern (procedure)")
        print("8  - Delete (name or phone)")
        print("9  - Delete via procedure")
        print("10 - Pagination")
        print("11 - Show all contacts")
        print("0  - Exit")

        choice = input("Choose: ")

        if choice == "1":
            insert_from_csv("../Practice7/contacts.csv")   # path goes up one folder then into Practice7
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            insert_or_update()
        elif choice == "4":
            insert_many_users()
        elif choice == "5":
            update_contact()
        elif choice == "6":
            query_contacts()
        elif choice == "7":
            search_pattern()
        elif choice == "8":
            delete_contact()
        elif choice == "9":
            delete_user()
        elif choice == "10":
            pagination()
        elif choice == "11":
            show_all_contacts()
        elif choice == "0":
            print("Bye!")
            break       # exit the while loop and end program
        else:
            print("Wrong choice")


if __name__ == "__main__":   # run menu() only when file is executed directly, not imported
    menu()