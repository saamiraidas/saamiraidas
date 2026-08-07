import os
import sqlite3
from dotenv import load_dotenv
from supabase import create_client

import streamlit as st
import pandas as pd

# Load environment variables for Supabase
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    if not SUPABASE_URL:
        SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    if not SUPABASE_KEY:
        SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
except Exception:
    pass

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        supabase = None

# Local SQLite database connection
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "emis.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()


def table_exists(table_name: str) -> bool:
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def check_db_available() -> bool:
    if supabase is None:
        return False

    try:
        res = supabase.table("users").select("username").limit(1).execute()
        data = None
        if isinstance(res, dict):
            data = res.get("data")
        else:
            data = getattr(res, "data", None)
        return True if data is not None else False
    except Exception:
        return False


def db_get_user(username: str):
    if supabase is None:
        return None

    try:
        res = supabase.table("users").select("*").eq("username", username).limit(1).execute()
        if isinstance(res, dict):
            data = res.get("data")
        else:
            data = getattr(res, "data", None)

        if data and len(data) > 0:
            return data[0]
        return None
    except Exception:
        return None


# Demo fallback users
users = {
    "admin": {
        "password": "admin123",
        "school": "ABC Secondary School",
        "role": "Administrator"
    },
    "teacher": {
        "password": "teacher123",
        "school": "XYZ High School",
        "role": "Teacher"
    }
}


# Student functions

def ensure_students_table():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            class TEXT,
            section TEXT,
            gender TEXT,
            dob TEXT,
            phone TEXT,
            address TEXT
        )
        """
    )
    conn.commit()


def add_student(name, student_class, section, gender, dob, phone, address):
    cursor.execute(
        """
        INSERT INTO students (name, class, section, gender, dob, phone, address)
        VALUES(?,?,?,?,?,?,?)
        """,
        (name, student_class, section, gender, dob, phone, address)
    )
    conn.commit()

    if supabase is not None:
        try:
            supabase.table("students").insert({
                "name": name,
                "class": student_class,
                "section": section,
                "gender": gender,
                "dob": dob,
                "phone": phone,
                "address": address
            }).execute()
        except Exception:
            pass


def get_students():
    return pd.read_sql("SELECT * FROM students", conn)


def delete_student(student_id):
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()


def student_management():
    st.title("👨‍🎓 Student Management System")
    ensure_students_table()

    menu = st.sidebar.radio(
        "Student Menu",
        ["Add Student", "View Students", "Search Student", "Delete Student"]
    )

    if menu == "Add Student":
        st.subheader("➕ Add New Student")
        name = st.text_input("Student Name")
        student_class = st.selectbox("Class", ["Nursery", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        section = st.selectbox("Section", ["A", "B", "C"])
        gender = st.radio("Gender", ["Male", "Female"])
        dob = st.date_input("Date of Birth")
        phone = st.text_input("Phone Number")
        address = st.text_area("Address")

        if st.button("Save Student"):
            add_student(name, student_class, section, gender, str(dob), phone, address)
            st.success("Student added successfully")

    elif menu == "View Students":
        st.subheader("📋 Student Records")
        data = get_students()
        st.dataframe(data, use_container_width=True)

    elif menu == "Search Student":
        st.subheader("🔍 Search Student")
        keyword = st.text_input("Enter Student Name")
        if keyword:
            result = pd.read_sql(
                "SELECT * FROM students WHERE name LIKE ?",
                conn,
                params=("%" + keyword + "%",)
            )
            st.dataframe(result, use_container_width=True)

    elif menu == "Delete Student":
        st.subheader("🗑️ Delete Student")
        students = get_students()
        if len(students) > 0:
            student_id = st.selectbox("Select Student ID", students["id"])
            if st.button("Delete"):
                delete_student(student_id)
                st.success("Student deleted successfully")
        else:
            st.warning("No student records found")


# Teacher functions

def ensure_teachers_table():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS teachers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            subject TEXT,
            qualification TEXT,
            phone TEXT,
            email TEXT,
            address TEXT
        )
        """
    )
    conn.commit()


def add_teacher(name, gender, subject, qualification, phone, email, address):
    cursor.execute(
        """
        INSERT INTO teachers (name, gender, subject, qualification, phone, email, address)
        VALUES(?,?,?,?,?,?,?)
        """,
        (name, gender, subject, qualification, phone, email, address)
    )
    conn.commit()

    if supabase is not None:
        try:
            supabase.table("teachers").insert({
                "name": name,
                "gender": gender,
                "subject": subject,
                "qualification": qualification,
                "phone": phone,
                "email": email,
                "address": address
            }).execute()
        except Exception:
            pass


def get_teachers():
    return pd.read_sql("SELECT * FROM teachers", conn)


def delete_teacher(teacher_id):
    cursor.execute("DELETE FROM teachers WHERE id=?", (teacher_id,))
    conn.commit()


def teacher_management():
    st.title("👩‍🏫 Teacher Management System")
    ensure_teachers_table()

    menu = st.sidebar.radio(
        "Teacher Menu",
        ["Add Teacher", "View Teachers", "Search Teacher", "Delete Teacher"]
    )

    if menu == "Add Teacher":
        st.subheader("➕ Add New Teacher")
        name = st.text_input("Teacher Name")
        gender = st.radio("Gender", ["Male", "Female"])
        subject = st.selectbox("Subject", ["English", "Nepali", "Mathematics", "Science", "Social Studies", "Computer"])
        qualification = st.text_input("Qualification")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        address = st.text_area("Address")

        if st.button("Save Teacher"):
            add_teacher(name, gender, subject, qualification, phone, email, address)
            st.success("Teacher added successfully")

    elif menu == "View Teachers":
        st.subheader("📋 Teacher Records")
        data = get_teachers()
        st.dataframe(data, use_container_width=True)

    elif menu == "Search Teacher":
        st.subheader("🔍 Search Teacher")
        keyword = st.text_input("Enter Teacher Name")
        if keyword:
            result = pd.read_sql(
                "SELECT * FROM teachers WHERE name LIKE ?",
                conn,
                params=("%" + keyword + "%",)
            )
            st.dataframe(result, use_container_width=True)

    elif menu == "Delete Teacher":
        st.subheader("🗑 Delete Teacher")
        teachers = get_teachers()
        if len(teachers) > 0:
            teacher_id = st.selectbox("Select Teacher ID", teachers["id"])
            if st.button("Delete"):
                delete_teacher(teacher_id)
                st.success("Teacher deleted successfully")
        else:
            st.warning("No teacher records found")


# Fee functions

def ensure_fees_table():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS fees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            student_name TEXT NOT NULL,
            class TEXT NOT NULL,
            total_fee REAL NOT NULL,
            paid_fee REAL NOT NULL,
            due_fee REAL NOT NULL,
            payment_status TEXT NOT NULL,
            payment_date TEXT
        )
        """
    )
    conn.commit()


def add_fee(student_id, student_name, student_class, total_fee, paid_fee, payment_date):
    due_fee = float(total_fee) - float(paid_fee)
    status = "Paid" if due_fee <= 0 else "Due"

    cursor.execute(
        """
        INSERT INTO fees (student_id, student_name, class, total_fee, paid_fee, due_fee, payment_status, payment_date)
        VALUES(?,?,?,?,?,?,?,?)
        """,
        (student_id, student_name, student_class, total_fee, paid_fee, due_fee, status, payment_date)
    )
    conn.commit()

    if supabase is not None:
        try:
            supabase.table("fees").insert({
                "student_id": student_id,
                "student_name": student_name,
                "class": student_class,
                "total_fee": total_fee,
                "paid_fee": paid_fee,
                "due_fee": due_fee,
                "payment_status": status,
                "payment_date": payment_date
            }).execute()
        except Exception:
            pass


def get_fees():
    return pd.read_sql("SELECT * FROM fees", conn)


def search_fee(keyword):
    return pd.read_sql(
        "SELECT * FROM fees WHERE student_name LIKE ?",
        conn,
        params=("%" + keyword + "%",)
    )


def update_status(fee_id, status):
    cursor.execute("UPDATE fees SET payment_status=? WHERE id=?", (status, fee_id))
    conn.commit()


def delete_fee(fee_id):
    cursor.execute("DELETE FROM fees WHERE id=?", (fee_id,))
    conn.commit()


def fee_management():
    ensure_fees_table()
    st.title("💰 Student Fee Management System")

    menu = st.sidebar.radio(
        "Fees Menu",
        ["Add Fee", "View Fee", "Search Fee", "Update Status", "Delete Fee"]
    )

    if menu == "Add Fee":
        st.subheader("➕ Add Student Fee")
        student_id = st.number_input("Student ID", min_value=1)
        student_name = st.text_input("Student Name")
        student_class = st.selectbox("Class", ["Nursery", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        total_fee = st.number_input("Total Fee", min_value=0.0)
        paid_fee = st.number_input("Paid Fee", min_value=0.0)
        payment_date = st.date_input("Payment Date")

        if st.button("Save Fee"):
            add_fee(student_id, student_name, student_class, total_fee, paid_fee, str(payment_date))
            st.success("Fee added successfully")

    elif menu == "View Fee":
        st.subheader("📋 Fee Records")
        data = get_fees()
        st.dataframe(data, use_container_width=True)

    elif menu == "Search Fee":
        st.subheader("🔍 Search Student Fee")
        keyword = st.text_input("Enter Student Name")
        if keyword:
            result = search_fee(keyword)
            st.dataframe(result, use_container_width=True)

    elif menu == "Update Status":
        st.subheader("✏ Update Payment Status")
        data = get_fees()
        if len(data) > 0:
            fee_id = st.selectbox("Select Fee ID", data["id"])
            status = st.selectbox("Payment Status", ["Paid", "Due"])
            if st.button("Update"):
                update_status(fee_id, status)
                st.success("Status updated")
        else:
            st.warning("No fee records found")

    elif menu == "Delete Fee":
        st.subheader("🗑 Delete Fee")
        data = get_fees()
        if len(data) > 0:
            fee_id = st.selectbox("Select Fee ID", data["id"])
            if st.button("Delete"):
                delete_fee(fee_id)
                st.success("Fee deleted successfully")
        else:
            st.warning("No fee records found")


# Librarian functions

def ensure_librarians_table():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS librarians(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            qualification TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            joining_date TEXT
        )
        """
    )
    conn.commit()


def add_librarian(name, gender, qualification, phone, email, address, joining_date):
    cursor.execute(
        """
        INSERT INTO librarians (name, gender, qualification, phone, email, address, joining_date)
        VALUES(?,?,?,?,?,?,?)
        """,
        (name, gender, qualification, phone, email, address, joining_date)
    )
    conn.commit()

    if supabase is not None:
        try:
            supabase.table("librarians").insert({
                "name": name,
                "gender": gender,
                "qualification": qualification,
                "phone": phone,
                "email": email,
                "address": address,
                "joining_date": joining_date
            }).execute()
        except Exception:
            pass


def get_librarians():
    return pd.read_sql("SELECT * FROM librarians", conn)


def update_librarian(lid, name, gender, qualification, phone, email, address, joining_date):
    cursor.execute(
        """
        UPDATE librarians SET name=?, gender=?, qualification=?, phone=?, email=?, address=?, joining_date=?
        WHERE id=?
        """,
        (name, gender, qualification, phone, email, address, joining_date, lid)
    )
    conn.commit()


def delete_librarian(lid):
    cursor.execute("DELETE FROM librarians WHERE id=?", (lid,))
    conn.commit()


def librarian_management():
    st.title("📚 Librarian Management System")
    ensure_librarians_table()

    menu = st.sidebar.radio(
        "Librarian Menu",
        ["Add Librarian", "View Librarian", "Search Librarian", "Update Librarian", "Delete Librarian"]
    )

    if menu == "Add Librarian":
        st.subheader("➕ Add Librarian Details")
        name = st.text_input("Librarian Name")
        gender = st.selectbox("Gender", ["Male", "Female"])
        qualification = st.text_input("Qualification")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        address = st.text_area("Address")
        joining_date = st.date_input("Joining Date")

        if st.button("Save Librarian"):
            add_librarian(name, gender, qualification, phone, email, address, str(joining_date))
            st.success("Librarian added successfully")

    elif menu == "View Librarian":
        st.subheader("📋 Librarian Records")
        data = get_librarians()
        st.dataframe(data, use_container_width=True)

    elif menu == "Search Librarian":
        st.subheader("🔍 Search Librarian")
        keyword = st.text_input("Enter Librarian Name")
        if keyword:
            result = pd.read_sql(
                "SELECT * FROM librarians WHERE name LIKE ?",
                conn,
                params=("%" + keyword + "%",)
            )
            st.dataframe(result, use_container_width=True)

    elif menu == "Update Librarian":
        st.subheader("✏ Update Librarian")
        data = get_librarians()
        if len(data) > 0:
            lid = st.selectbox("Select Librarian ID", data["id"])
            record = data[data["id"] == lid].iloc[0]
            name = st.text_input("Name", record["name"])
            gender = st.text_input("Gender", record["gender"])
            qualification = st.text_input("Qualification", record["qualification"])
            phone = st.text_input("Phone", record["phone"])
            email = st.text_input("Email", record["email"])
            address = st.text_area("Address", record["address"])
            joining_date = st.text_input("Joining Date", record["joining_date"])

            if st.button("Update"):
                update_librarian(lid, name, gender, qualification, phone, email, address, joining_date)
                st.success("Librarian updated successfully")
        else:
            st.warning("No librarian records found")

    elif menu == "Delete Librarian":
        st.subheader("🗑 Delete Librarian")
        data = get_librarians()
        if len(data) > 0:
            lid = st.selectbox("Select Librarian ID", data["id"])
            if st.button("Delete"):
                delete_librarian(lid)
                st.success("Librarian deleted successfully")
        else:
            st.warning("No librarian records found")


# Accountant functions

def ensure_accountants_table():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS accountants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            qualification TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            joining_date TEXT,
            salary INTEGER
        )
        """
    )
    conn.commit()

    columns = [row[1] for row in cursor.execute("PRAGMA table_info(accountants)").fetchall()]
    for column_name, column_type in [
        ("gender", "TEXT"),
        ("qualification", "TEXT"),
        ("address", "TEXT"),
        ("joining_date", "TEXT"),
        ("salary", "INTEGER")
    ]:
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE accountants ADD COLUMN {column_name} {column_type}")
    conn.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='accountant'")
    if cursor.fetchone():
        cursor.execute("SELECT count(*) FROM accountants")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO accountants (id, name, email, phone, salary) "
                "SELECT id, name, email, phone, salary FROM accountant"
            )
            conn.commit()


def add_accountant(name, gender, qualification, phone, email, address, joining_date):
    cursor.execute(
        """
        INSERT INTO accountants (name, gender, qualification, phone, email, address, joining_date)
        VALUES(?,?,?,?,?,?,?)
        """,
        (name, gender, qualification, phone, email, address, joining_date)
    )
    conn.commit()

    if supabase is not None:
        try:
            supabase.table("accountants").insert({
                "name": name,
                "gender": gender,
                "qualification": qualification,
                "phone": phone,
                "email": email,
                "address": address,
                "joining_date": joining_date
            }).execute()
        except Exception:
            pass


def get_accountants():
    if not table_exists("accountants"):
        ensure_accountants_table()
    return pd.read_sql("SELECT * FROM accountants", conn)


def update_accountant(aid, name, gender, qualification, phone, email, address, joining_date):
    cursor.execute(
        """
        UPDATE accountants SET name=?, gender=?, qualification=?, phone=?, email=?, address=?, joining_date=?
        WHERE id=?
        """,
        (name, gender, qualification, phone, email, address, joining_date, aid)
    )
    conn.commit()


def delete_accountant(aid):
    cursor.execute("DELETE FROM accountants WHERE id=?", (aid,))
    conn.commit()


def accountant_management():
    st.title("💰 Accountant Management System")
    ensure_accountants_table()

    menu = st.sidebar.radio(
        "Accountant Menu",
        ["Add Accountant", "View Accountant", "Search Accountant", "Update Accountant", "Delete Accountant"]
    )

    if menu == "Add Accountant":
        st.subheader("➕ Add Accountant Details")
        name = st.text_input("Accountant Name")
        gender = st.selectbox("Gender", ["Male", "Female"])
        qualification = st.text_input("Qualification")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        address = st.text_area("Address")
        joining_date = st.date_input("Joining Date")

        if st.button("Save Accountant"):
            add_accountant(name, gender, qualification, phone, email, address, str(joining_date))
            st.success("Accountant added successfully")

    elif menu == "View Accountant":
        st.subheader("📋 Accountant Records")
        data = get_accountants()
        st.dataframe(data, use_container_width=True)

    elif menu == "Search Accountant":
        st.subheader("🔍 Search Accountant")
        keyword = st.text_input("Enter Accountant Name")
        if keyword:
            result = pd.read_sql(
                "SELECT * FROM accountants WHERE name LIKE ?",
                conn,
                params=("%" + keyword + "%",)
            )
            st.dataframe(result, use_container_width=True)

    elif menu == "Update Accountant":
        st.subheader("✏ Update Accountant")
        data = get_accountants()
        if len(data) > 0:
            aid = st.selectbox("Select Accountant ID", data["id"])
            record = data[data["id"] == aid].iloc[0]
            name = st.text_input("Name", record["name"])
            gender = st.text_input("Gender", record["gender"])
            qualification = st.text_input("Qualification", record["qualification"])
            phone = st.text_input("Phone", record["phone"])
            email = st.text_input("Email", record["email"])
            address = st.text_area("Address", record["address"])
            joining_date = st.text_input("Joining Date", record["joining_date"])

            if st.button("Update"):
                update_accountant(aid, name, gender, qualification, phone, email, address, joining_date)
                st.success("Accountant updated successfully")
        else:
            st.warning("No accountant records found")

    elif menu == "Delete Accountant":
        st.subheader("🗑 Delete Accountant")
        data = get_accountants()
        if len(data) > 0:
            aid = st.selectbox("Select Accountant ID", data["id"])
            if st.button("Delete"):
                delete_accountant(aid)
                st.success("Accountant deleted successfully")
        else:
            st.warning("No accountant records found")


# Principal functions

def ensure_principal_table():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS principal(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            qualification TEXT,
            experience TEXT,
            phone TEXT,
            email TEXT,
            address TEXT
        )
        """
    )
    conn.commit()


def add_principal(name, gender, qualification, experience, phone, email, address):
    cursor.execute(
        """
        INSERT INTO principal (name, gender, qualification, experience, phone, email, address)
        VALUES(?,?,?,?,?,?,?)
        """,
        (name, gender, qualification, experience, phone, email, address)
    )
    conn.commit()

    if supabase is not None:
        try:
            supabase.table("principal").insert({
                "name": name,
                "gender": gender,
                "qualification": qualification,
                "experience": experience,
                "phone": phone,
                "email": email,
                "address": address
            }).execute()
        except Exception:
            pass


def get_principal():
    return pd.read_sql("SELECT * FROM principal", conn)


def update_principal(pid, name, gender, qualification, experience, phone, email, address):
    cursor.execute(
        """
        UPDATE principal SET name=?, gender=?, qualification=?, experience=?, phone=?, email=?, address=?
        WHERE id=?
        """,
        (name, gender, qualification, experience, phone, email, address, pid)
    )
    conn.commit()


def delete_principal(pid):
    cursor.execute("DELETE FROM principal WHERE id=?", (pid,))
    conn.commit()


def principal_management():
    st.title("👨‍💼 Principal Management System")
    ensure_principal_table()

    menu = st.sidebar.radio(
        "Principal Menu",
        ["Add Principal", "View Principal", "Update Principal", "Delete Principal"]
    )

    if menu == "Add Principal":
        st.subheader("➕ Add Principal Details")
        name = st.text_input("Principal Name")
        gender = st.selectbox("Gender", ["Male", "Female"])
        qualification = st.text_input("Qualification")
        experience = st.text_input("Experience (Years)")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        address = st.text_area("Address")

        if st.button("Save Principal"):
            add_principal(name, gender, qualification, experience, phone, email, address)
            st.success("Principal added successfully")

    elif menu == "View Principal":
        st.subheader("📋 Principal Information")
        data = get_principal()
        st.dataframe(data, use_container_width=True)

    elif menu == "Update Principal":
        st.subheader("✏ Update Principal")
        data = get_principal()
        if len(data) > 0:
            pid = st.selectbox("Select Principal ID", data["id"])
            record = data[data["id"] == pid].iloc[0]
            name = st.text_input("Name", record["name"])
            gender = st.text_input("Gender", record["gender"])
            qualification = st.text_input("Qualification", record["qualification"])
            experience = st.text_input("Experience", record["experience"])
            phone = st.text_input("Phone", record["phone"])
            email = st.text_input("Email", record["email"])
            address = st.text_area("Address", record["address"])

            if st.button("Update"):
                update_principal(pid, name, gender, qualification, experience, phone, email, address)
                st.success("Principal updated successfully")
        else:
            st.warning("No principal record found")

    elif menu == "Delete Principal":
        st.subheader("🗑 Delete Principal")
        data = get_principal()
        if len(data) > 0:
            pid = st.selectbox("Select Principal ID", data["id"])
            if st.button("Delete"):
                delete_principal(pid)
                st.success("Principal deleted successfully")
        else:
            st.warning("No principal record found")


# Login and dashboard
st.set_page_config(page_title="EMIS School Management System", page_icon="🏫", layout="centered")

st.session_state.setdefault("logged_in", False)
st.session_state.setdefault("username", "")
st.session_state.setdefault("school", "")
st.session_state.setdefault("role", "")


def login_page():
    st.markdown(
        "<h1 style='text-align:center;color:#1f77b4;'>🏫 EMIS School Management System</h1>",
        unsafe_allow_html=True
    )
    st.write("")

    with st.container():
        st.subheader("🔐 School Login")
        school_id = st.text_input("School ID", placeholder="Enter School ID")
        username = st.text_input("Username", placeholder="Enter Username")
        password = st.text_input("Password", type="password", placeholder="Enter Password")

        db_available = check_db_available()
        if db_available:
            st.success("Connected to database")
        else:
            st.warning("Database not available — using local demo users")

        if st.button("Login", use_container_width=True):
            authenticated = False
            if db_available:
                user = db_get_user(username)
                if user and str(user.get("password", "")) == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.school = user.get("school", "Unknown School")
                    st.session_state.role = user.get("role", "User")
                    authenticated = True

            if not authenticated and username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.school = users[username]["school"]
                st.session_state.role = users[username]["role"]
                authenticated = True

            if authenticated:
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")


def dashboard():
    st.sidebar.title("EMIS Menu")
    menu = st.sidebar.selectbox(
        "Select Module",
        [
            "Dashboard",
            "Student Management",
            "Teacher Management",
            "Fee Management",
            "Librarian Management",
            "Accountant Management",
            "Principal Management",
            "Attendance",
            "Examination",
            "Reports"
        ]
    )
    st.sidebar.write("---")
    st.sidebar.write(f"User: {st.session_state.username}")
    st.sidebar.write(f"Role: {st.session_state.role}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📊 EMIS Dashboard")
    st.info(f"""
        School: {st.session_state.school}

        Role: {st.session_state.role}
        """)

    if menu == "Student Management":
        student_management()
    elif menu == "Teacher Management":
        teacher_management()
    elif menu == "Fee Management":
        fee_management()
    elif menu == "Librarian Management":
        librarian_management()
    elif menu == "Accountant Management":
        accountant_management()
    elif menu == "Principal Management":
        principal_management()
    elif menu == "Attendance":
        st.subheader("📅 Attendance System")
        st.write("Record daily attendance.")
    elif menu == "Examination":
        st.subheader("📝 Examination Module")
        st.write("Manage marks and results.")
    elif menu == "Reports":
        st.subheader("📈 Reports")
        st.write("Generate school reports.")
    else:
        st.subheader("Welcome to EMIS")


if st.session_state.logged_in:
    dashboard()
else:
    login_page()
