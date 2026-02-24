import datetime
import hashlib

import mysql.connector
import pandas as pd
import streamlit as st

# DB CONNECTION 

def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",          # MySQL user
        password="Abhi@2026", # MySQL password
        database="client_query_db"
    )
    return conn


def load_queries():
    conn = get_connection()
    query = """
        SELECT 
            id,
            query_id,
            client_email,
            client_mobile,
            query_heading,
            query_description,
            status,
            date_raised,
            date_closed
        FROM client_queries
        ORDER BY date_raised DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


#  USER AUTHENTICATION

def hash_password(plain_password: str) -> str:
    return hashlib.sha256(plain_password.encode()).hexdigest()


def get_user(username: str):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT username, hashed_password, role
        FROM users
        WHERE username = %s
    """
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


# SIDEBAR: LOGIN / LOGOUT

st.sidebar.title("Client Query Management System")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

if not st.session_state.logged_in:
    st.sidebar.subheader("Login")

    input_username = st.sidebar.text_input("Username")
    input_password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        user = get_user(input_username)
        if user is None:
            st.sidebar.error("User not found.")
        else:
            db_username, db_hashed_password, db_role = user
            if hash_password(input_password) == db_hashed_password:
                st.session_state.logged_in = True
                st.session_state.role = db_role
                st.session_state.username = db_username
                st.rerun()
            else:
                st.sidebar.error("Incorrect password.")

else:
    st.sidebar.write(
        f"Logged in as {st.session_state.username} ({st.session_state.role})"
    )
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.username = None
        st.rerun()



# MAIN VIEW (ROLE-BASED)

if not st.session_state.logged_in:
    st.title("Please log in to continue.")
else:
    role = st.session_state.role

    # FOR CLIENT PAGE
    if role == "client":
        st.title("Client - Submit a New Query")

        client_email = st.text_input("Email ID")
        client_mobile = st.text_input("Mobile Number")
        query_heading = st.text_input("Query Heading")
        query_description = st.text_area("Query Description")

        if st.button("Submit Query"):
            if (
                not client_email
                or not client_mobile
                or not query_heading
                or not query_description
            ):
                st.warning("Please fill all fields.")
            else:
                conn = get_connection()
                cursor = conn.cursor()

                get_max_id_query = "SELECT MAX(id) FROM client_queries"
                cursor.execute(get_max_id_query)
                max_id = cursor.fetchone()[0]
                if max_id is None:
                    max_id = 0
                new_id_num = max_id + 1
                new_query_id = f"Q{new_id_num:04d}"

                insert_query = """
                    INSERT INTO client_queries
                    (query_id, client_email, client_mobile,
                     query_heading, query_description,
                     status, date_raised, date_closed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """

                now = datetime.datetime.now()

                cursor.execute(
                    insert_query,
                    (
                        new_query_id,
                        client_email,
                        client_mobile,
                        query_heading,
                        query_description,
                        "Opened",
                        now,
                        None,
                    ),
                )

                conn.commit()
                cursor.close()
                conn.close()

                st.success(
                    f"Your query has been submitted! "
                    f"Your Query ID is {new_query_id}."
                )

    # For SUPPORT PAGE
    elif role == "support":
        st.title("Support Dashboard")

        df = load_queries()

        
        total_queries = len(df)
        open_queries = (df["status"] == "Opened").sum()
        closed_queries = (df["status"] == "Closed").sum()

        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Queries", total_queries)
        col2.metric("Open Queries", open_queries)
        col3.metric("Closed Queries", closed_queries)

        # Query list with filter
        st.subheader("Query List")

        status_filter = st.selectbox(
            "Filter by status",
            options=["All", "Opened", "Closed"],
            index=0,
        )

        if status_filter != "All":
            filtered_df = df[df["status"] == status_filter]
        else:
            filtered_df = df

        st.dataframe(filtered_df)

        # Close by ID
        st.subheader("Close a Query")

        query_id_to_close = st.number_input(
            "Enter row ID to close (id column, e.g., 1254)",
            min_value=1,
            step=1,
        )

        if st.button("Close Query by ID"):
            conn = get_connection()
            cursor = conn.cursor(buffered=True)

            check_query = """
                SELECT query_id, status FROM client_queries
                WHERE id = %s
            """
            cursor.execute(check_query, (int(query_id_to_close),))
            result = cursor.fetchone()

            if result is None:
                st.error("No query found with this ID.")
            else:
                qid, current_status = result
                if current_status == "Closed":
                    st.info(
                        f"Query {qid} (id={query_id_to_close}) "
                        f"is already closed."
                    )
                else:
                    update_query = """
                        UPDATE client_queries
                        SET status = 'Closed',
                            date_closed = %s
                        WHERE id = %s
                    """
                    now = datetime.datetime.now()
                    cursor.execute(
                        update_query,
                        (now, int(query_id_to_close)),
                    )
                    conn.commit()
                    st.success(
                        f"Query {qid} (id={query_id_to_close}) "
                        f"closed successfully at {now}."
                    )

            cursor.close()
            conn.close()

            st.rerun()


        # Insights
        st.subheader("Insights")

        closed_df = df[df["status"] == "Closed"].copy()

        if not closed_df.empty:
            closed_df["resolution_days"] = (
                closed_df["date_closed"] - closed_df["date_raised"]
            ).dt.days

            avg_resolution = closed_df["resolution_days"].mean()
            max_resolution = closed_df["resolution_days"].max()
            min_resolution = closed_df["resolution_days"].min()

            st.write(f"Average resolution time: {avg_resolution:.2f} days")
            st.write(f"Fastest resolution time: {min_resolution} days")
            st.write(f"Slowest resolution time: {max_resolution} days")

            type_counts = closed_df["query_heading"].value_counts().head(5)
            st.write("Top 5 query types (Closed):")
            st.bar_chart(type_counts)
        else:
            st.info("No closed queries available yet for insights.")
