import streamlit as st
import mysql.connector
from datetime import datetime
# Set page configuration
st.set_page_config(page_title="To-Do List Manager", layout="centered")

st.markdown(
    """
    <style>
    /* Force dark background */
    html, body, [class*="css"] {
        background-color: #0e1117 !important;
        color: #e6e6e6 !important;
    }

    /* Main content area */
    section[data-testid="stAppViewContainer"] {
        background-color: #0e1117 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0b0f14 !important;
    }

    /* Text inputs, select boxes */
    input, textarea, select {
        background-color: #111827 !important;
        color: #e6e6e6 !important;
        border: 1px solid #00FFFF !important; /* aqua border */
    }

    /* Buttons */
    button {
        background-color: #00FFFF !important; /* aqua button */
        color: #000000 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    button:hover {
        background-color: #00CED1 !important; /* darker aqua on hover */
        color: #000000 !important;
    }

    /* Headings (aqua theme) */
    h1, h2, h3, h4, h5, h6 {
        color: #00FFFF !important;
    }

    /* Hide Streamlit header & footer */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)



# ---------------- DB CONNECTION ----------------
def connect_db(db=None):
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database=db
    )

# ---------------- DB & TABLE SETUP ----------------
def setup_database():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )
    cur = con.cursor()

    cur.execute("CREATE DATABASE IF NOT EXISTS todo_db")
    cur.execute("USE todo_db")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50),
        email VARCHAR(50) UNIQUE,
        password VARCHAR(50)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        task TEXT,
        created_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    con.commit()
    cur.close()
    con.close()

setup_database()

# ---------------- USER FUNCTIONS ----------------
def register_user(name, email, password):
    con = connect_db("todo_db")
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        con.commit()
        return True
    except:
        return False
    finally:
        cur.close()
        con.close()

def login_user(email, password):
    con = connect_db("todo_db")
    cur = con.cursor()
    cur.execute(
        "SELECT id FROM users WHERE email=%s AND password=%s",
        (email, password)
    )
    user = cur.fetchone()
    cur.close()
    con.close()
    return user

# ---------------- TASK FUNCTIONS ----------------
def add_task(user_id, task):
    con = connect_db("todo_db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO tasks (user_id, task, created_at) VALUES (%s, %s, %s)",
        (user_id, task, datetime.now())
    )
    con.commit()
    cur.close()
    con.close()

def view_tasks(user_id):
    con = connect_db("todo_db")
    cur = con.cursor()
    cur.execute(
        "SELECT id, task, created_at FROM tasks WHERE user_id=%s",
        (user_id,)
    )
    data = cur.fetchall()
    cur.close()
    con.close()
    return data

def update_task(task_id, new_task):
    con = connect_db("todo_db")
    cur = con.cursor()
    cur.execute(
        "UPDATE tasks SET task=%s WHERE id=%s",
        (new_task, task_id)
    )
    con.commit()
    cur.close()
    con.close()

def delete_task(task_id):
    con = connect_db("todo_db")
    cur = con.cursor()
    cur.execute(
        "DELETE FROM tasks WHERE id=%s",
        (task_id,)
    )
    con.commit()
    cur.close()
    con.close()


# ---------------- SESSION ----------------
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------------- UI ----------------
st.title("📝 To-Do List Manager")

# ---------- SIDEBAR MENU ----------
if st.session_state.user_id is None:
    menu = st.sidebar.selectbox("Menu", ["Home", "Register", "Login"])
else:
    menu = st.sidebar.selectbox("Menu", ["Home","Add Task", "View Task", "Logout"])


# --------------- HOME ----------------
if menu == "Home":
    st.subheader("🏠 Home Page")
    st.write("Welcome to the To-Do List Manager!")
    st.write("👉 Create a new account by registering")
    st.write("👉 Log in to manage your tasks")


# ---------------- REGISTER ----------------
if menu == "Register":
    st.subheader("Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if register_user(name, email, password):
            st.success("Registered Successfully")
        else:
            st.error("Email already exists")

# ---------------- LOGIN ----------------
elif menu == "Login":
    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email == "" or password == "":
            st.warning("Please enter both email and password")
        else:
              user = login_user(email, password)
              if user:
                  st.session_state.user_id = user[0]
                  st.success("Login Successful")
                  st.rerun()
              else:
                  st.error("Invalid Email or Password")
# ---------------- ADD TASK ----------------
elif menu == "Add Task":
    st.subheader("Add Task")

    task = st.text_area("Enter Task")

    if st.button("Add"):
        add_task(st.session_state.user_id, task)
        st.success("Task Added")

# ---------------- VIEW TASK ----------------
elif menu == "View Task":
    st.subheader("Your Tasks")

    tasks = view_tasks(st.session_state.user_id)

    if not tasks:
        st.info("No tasks found")
    else:
        for task_id, task_text, created_at in tasks:
            col1, col2, col3 = st.columns([6, 2, 2])

            with col1:
                st.write(f"🟢 {task_text} ({created_at})")

            with col2:
                if st.button("✏️ Edit", key=f"edit_{task_id}"):
                    st.session_state.edit_id = task_id
                    st.session_state.edit_text = task_text

            with col3:
                if st.button("🗑️ Delete", key=f"del_{task_id}"):
                    delete_task(task_id)
                    st.success("Task deleted")
                    st.rerun()

    # ----- EDIT SECTION -----
    if "edit_id" in st.session_state:
        st.subheader("Edit Task")

        new_task = st.text_input(
            "Update Task",
            st.session_state.edit_text
        )

        if st.button("Update Task"):
            update_task(st.session_state.edit_id, new_task)
            del st.session_state.edit_id
            del st.session_state.edit_text
            st.success("Task updated")
            st.rerun()

# ---------------- LOGOUT ----------------
elif menu == "Logout":
    st.session_state.user_id = None
    st.success("Logged Out")
    st.rerun()

