import mysql.connector
from datetime import datetime
from getpass import getpass

def connect_db():
    # Hardcode your password here temporarily
    password = "Raj@2904"  # CHANGE THIS to your actual MySQL root password
    
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password=password,
            database="personal_manager",
            charset='utf8mb4',
            use_pure=True
        )
        print("✓ Connected successfully!")
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        print(f"Tried password: {password}")
        return None

def add_document(conn):
    try:
        cursor = conn.cursor()
        user_id = int(input("Enter user ID: "))
        document_name = input("Enter document name: ")
        authority = input("Enter authority: ")
        issue_date = input("Enter issue date (YYYY-MM-DD): ")
        expiry_date = input("Enter expiry date (YYYY-MM-DD): ")
        importance = input("Enter importance: ")
        
        query = "INSERT INTO documents (user_id, document_name, authority, issue_date, expiry_date, importance) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (user_id, document_name, authority, issue_date, expiry_date, importance))
        conn.commit()
        print("Document added successfully!")
    except Exception as e:
        print(f"Error adding document: {e}")
    finally:
        cursor.close()

def display_expiring_documents(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expiring_documents")
        results = cursor.fetchall()
        
        if results:
            print("\n--- Expiring Documents (Next 30 Days) ---")
            for row in results:
                print(f"ID: {row[0]}, User: {row[1]}, Name: {row[2]}, Authority: {row[3]}, Expiry: {row[5]}")
        else:
            print("No expiring documents found.")
    except Exception as e:
        print(f"Error displaying expiring documents: {e}")
    finally:
        cursor.close()

def get_upcoming_deadlines(conn):
    try:
        cursor = conn.cursor()
        cursor.callproc("get_upcoming_deadlines")
        
        print("\n--- Upcoming Deadlines (Next 7 Days) ---")
        for result in cursor.stored_results():
            rows = result.fetchall()
            if rows:
                for row in rows:
                    print(f"ID: {row[0]}, User: {row[1]}, Title: {row[2]}, Due: {row[4]}, Status: {row[5]}")
            else:
                print("No upcoming deadlines found.")
    except Exception as e:
        print(f"Error calling stored procedure: {e}")
    finally:
        cursor.close()

def add_goal(conn):
    try:
        cursor = conn.cursor()
        user_id = int(input("Enter user ID: "))
        goal_name = input("Enter goal name: ")
        start_date = input("Enter start date (YYYY-MM-DD): ")
        target_date = input("Enter target date (YYYY-MM-DD): ")
        progress = int(input("Enter progress (0-100): "))
        status = input("Enter status: ")
        
        query = "INSERT INTO goals (user_id, goal_name, start_date, target_date, progress, status) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (user_id, goal_name, start_date, target_date, progress, status))
        conn.commit()
        print("Goal added successfully!")
    except Exception as e:
        print(f"Error adding goal: {e}")
    finally:
        cursor.close()

def view_all_users(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, name, email, created_date FROM users")
        results = cursor.fetchall()
        if results:
            print("\n--- All Users ---")
            for row in results:
                print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Joined: {row[3]}")
        else:
            print("No users found.")
    except Exception as e:
        print(f"Error fetching users: {e}")
    finally:
        cursor.close()

def view_user_documents(conn):
    try:
        cursor = conn.cursor()
        user_id = int(input("Enter user ID to view documents: "))
        cursor.execute("SELECT * FROM documents WHERE user_id = %s", (user_id,))
        results = cursor.fetchall()
        if results:
            print(f"\n--- Documents for User {user_id} ---")
            for row in results:
                print(f"Doc ID: {row[0]}, Name: {row[2]}, Authority: {row[3]}, Issue: {row[4]}, Expiry: {row[5]}, Importance: {row[6]}")
        else:
            print("No documents found for this user.")
    except Exception as e:
        print(f"Error fetching documents: {e}")
    finally:
        cursor.close()

def main():
    conn = connect_db()
    if not conn:
        print("Failed to connect to database. Exiting.")
        return
    
    while True:
        print("\n=== Personal Manager ===")
        print("1. Add a new document")
        print("2. Display expiring documents")
        print("3. Get upcoming deadlines")
        print("4. Add a new goal")
        print("5. Admin: View all users")
        print("6. Admin: View user documents")
        print("7. Exit")
        
        try:
            choice = input("\nEnter your choice: ")
            
            if choice == "1":
                add_document(conn)
            elif choice == "2":
                display_expiring_documents(conn)
            elif choice == "3":
                get_upcoming_deadlines(conn)
            elif choice == "4":
                add_goal(conn)
            elif choice == "5":
                view_all_users(conn)
            elif choice == "6":
                view_user_documents(conn)
            elif choice == "7":
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-7.")
        except KeyboardInterrupt:
            print("\nProgram interrupted. Exiting.")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    conn.close()

if __name__ == "__main__":
    main()
