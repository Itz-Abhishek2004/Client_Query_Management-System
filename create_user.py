import hashlib

import mysql.connector


db_config = {
    "host": "localhost",
    "user": "root",          
    "password": "Abhi@2026", 
    "database": "client_query_db",
}

def get_connection():
    return mysql.connector.connect(**db_config)

def hash_password(plain_password: str) -> str:
    """Password ko SHA-256 se hash karta hai."""
    return hashlib.sha256(plain_password.encode()).hexdigest()

def create_user(username: str, plain_password: str, role: str):
    if role not in ("client", "support"):
        raise ValueError("Role must be 'client' or 'support'")

    conn = get_connection()
    cursor = conn.cursor()

    hashed = hash_password(plain_password)

    insert_query = """
        INSERT INTO users (username, hashed_password, role)
        VALUES (%s, %s, %s)
    """

    try:
        cursor.execute(insert_query, (username, hashed, role))
        conn.commit()
        print(f"User '{username}' with role '{role}' created successfully.")
    except mysql.connector.Error as e:
        print("Error creating user:", e)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    

    username = input("Enter username: ")
    password = input("Enter password: ")
    role = input("Enter role (client/support): ").strip().lower()

    create_user(username, password, role)

    print("User creation complete.")