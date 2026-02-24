# Client Query Management System (Streamlit + MySQL)

This is a simple Client Query Management System built using Python, Streamlit, and MySQL.  
Clients can log in to raise queries, and support users can log in to view, manage, and close those queries from a web dashboard.[web:48]

---

## Features

- Login with fixed users and roles (Client and Support).
- Client:
  - Raise a new query with basic details.
  - View all queries created by that client.
  - See the current status of each query (Open / Closed).
- Support:
  - View all client queries in a table.
  - See total, open, and closed query counts.
  - Close a query by its ID, which updates its status and closed time.
- All data is stored in a MySQL database, so queries stay saved even if the app restarts.[web:48]

---

## Demo Users

You can use these demo credentials:

- Client user  
  - Username: `Jeff Bezos`  
  - Password: `Jeff@2026`  
  - Role: Client  

- Support user  
  - Username: `Ben Martin`  
  - Password: `Ben@2026`  
  - Role: Support  

These users are stored in the MySQL `users` table for testing.

---

## Tech Stack

- Python  
- Streamlit  
- MySQL  
- mysql-connector-python  
- pandas[web:48]

---

## How to Run

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
