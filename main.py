import streamlit as st
import sqlite3
import pandas as pd

# -------------------------
# Database
# -------------------------
conn = sqlite3.connect("students.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    course TEXT,
    marks REAL
)
""")
conn.commit()


# -------------------------
# Functions
# -------------------------
def add_student(name, age, gender, course, marks):
    cursor.execute(
        "INSERT INTO students(name, age, gender, course, marks) VALUES (?, ?, ?, ?, ?)",
        (name, age, gender, course, marks),
    )
    conn.commit()


def get_students():
    cursor.execute("SELECT * FROM students")
    return cursor.fetchall()


def update_student(student_id, name, age, gender, course, marks):
    cursor.execute(
        """
        UPDATE students
        SET name=?, age=?, gender=?, course=?, marks=?
        WHERE id=?
        """,
        (name, age, gender, course, marks, student_id),
    )
    conn.commit()


def delete_student(student_id):
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()


def search_student(name):
    cursor.execute(
        "SELECT * FROM students WHERE name LIKE ?",
        ('%' + name + '%',)
    )
    return cursor.fetchall()


# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Student Management System", layout="wide")

st.title("🎓 Student Management System")

menu = [
    "Add Student",
    "View Students",
    "Update Student",
    "Delete Student",
    "Search Student",
]

choice = st.sidebar.selectbox("Menu", menu)

# -------------------------
# Add Student
# -------------------------
if choice == "Add Student":

    st.subheader("Add New Student")
    ID = st.text_input("ID")
    name = st.text_input("Name")
    age = st.number_input("Age", 1, 100, 18)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    course = st.text_input("Course")
    marks = st.number_input("Marks", 0.0, 100.0)

    if st.button("Add Student"):

        if name == "" or course == "":
            st.warning("Please fill all fields.")
        else:
            add_student(name, age, gender, course, marks)
            st.success("Student added successfully.")

# -------------------------
# View Students
# -------------------------
elif choice == "View Students":

    st.subheader("Student Records")

    students = get_students()

    if students:
        df = pd.DataFrame(
            students,
            columns=[
                "ID",
                "Name",
                "Age",
                "Gender",
                "Course",
                "Marks",
            ],
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No student records found.")

# -------------------------
# Update Student
# -------------------------
elif choice == "Update Student":

    st.subheader("Update Student")

    students = get_students()

    if students:

        ids = [student[0] for student in students]

        student_id = st.selectbox("Select Student ID", ids)

        student = None

        for s in students:
            if s[0] == student_id:
                student = s
                break

        name = st.text_input("Name", student[1])
        age = st.number_input("Age", 1, 100, student[2])
        gender = st.selectbox(
            "Gender",
            ["Male", "Female", "Other"],
            index=["Male", "Female", "Other"].index(student[3]),
        )
        course = st.text_input("Course", student[4])
        marks = st.number_input(
            "Marks",
            0.0,
            100.0,
            float(student[5]),
        )

        if st.button("Update"):
            update_student(student_id, name, age, gender, course, marks)
            st.success("Student updated successfully.")

    else:
        st.info("No students available.")
# -------------------------
# Delete Student
# -------------------------
elif choice == "Delete Student":

    st.subheader("Delete Student")

    students = get_students()

    if students:

        ids = [student[0] for student in students]

        student_id = st.selectbox("Student ID", ids)

        if st.button("Delete"):
            delete_student(student_id)
            st.success("Student deleted successfully.")

    else:
        st.info("No students available.")

# -------------------------
# Search Student
# -------------------------
elif choice == "Search Student":

    st.subheader("Search Student")

    keyword = st.text_input("Enter student name")

    if st.button("Search"):

        results = search_student(keyword)

        if results:

            df = pd.DataFrame(
                results,
                columns=[
                    "ID",
                    "Name",
                    "Age",
                    "Gender",
                    "Course",
                    "Marks",
                ],
            )

            st.dataframe(df, use_container_width=True)

        else:
            st.warning("No student found.")
