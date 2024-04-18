import sqlite3
import streamlit as st
import pandas as pd

# Define Streamlit app
def main():
    st.title("Student Profile Management System")

    # Sidebar menu for actions
    action = st.sidebar.selectbox("Select Action", ["Add Student", "Delete Student", "Update Student", "Display Students", "Add Batch", "Display Batches", "Delete Batch"])

    # Initialize database connection
    with sqlite3.connect("git.db") as conn:
        cursor = conn.cursor()

        # Create tables if they don't exist
        create_students_table(cursor, conn)
        create_batch_table(cursor, conn)

        if action == "Add Student":
            st.sidebar.write("---")
            add_student(cursor, conn)

        elif action == "Delete Student":
            st.sidebar.write("---")
            delete_student(cursor, conn)

        elif action == "Update Student":
            st.sidebar.write("---")
            update_student(cursor, conn)

        elif action == "Display Students":
            st.sidebar.write("---")
            display_students(cursor)

        elif action == "Add Batch":
            st.sidebar.write("---")
            add_batch(cursor, conn)

        elif action == "Display Batches":
            st.sidebar.write("---")
            display_batches(cursor)

        elif action == "Delete Batch":
            st.sidebar.write("---")
            delete_batch(cursor, conn)


def add_student(cursor, conn):
    st.header("Add Student")

    id_ = st.text_input("ID")
    name = st.text_input("Name")
    branch = st.text_input("Branch")
    college = st.text_input("College")
    batch_options = ['None'] + get_batch_options(cursor)  # Add 'None' option
    selected_batches = st.multiselect("Batches", batch_options)

    if st.button("Add Student"):
        if id_ and name and branch and college:
            cursor.execute("SELECT * FROM students WHERE id=?", (id_,))
            existing_student = cursor.fetchone()
            if existing_student:
                st.warning("Student ID already exists.")
            else:
                for batch in selected_batches:
                    cursor.execute("INSERT INTO students (id, name, branch, college, batch) VALUES (?, ?, ?, ?, ?)", (id_, name, branch, college, batch if batch != 'None' else None))
                conn.commit()
                st.success("Student added successfully.")
        else:
            st.warning("Please input ID, name, branch, and college.")


def get_batch_options(cursor):
    cursor.execute("SELECT id FROM batch")
    batches = cursor.fetchall()
    return [batch[0] for batch in batches]


def delete_student(cursor, conn):
    st.header("Delete Student")

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    if students:
        column_names = ["Serial No.", "ID", "Name", "Branch", "College", "Batch"]  # Define column titles with Serial No.
        df = pd.DataFrame(students, columns=["ID", "Name", "Branch", "College", "Batch"])  # Create DataFrame without Serial No.
        df.index = range(1, len(df) + 1)  # Start index from 1
        df.index.name = "Serial No."  # Set index name
        st.table(df)  # Display DataFrame as table
        selected_students = st.multiselect("Select Students to Delete", df["ID"].tolist())  # Select students by ID
        if st.button("Delete Selected"):
            for student_id in selected_students:
                cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
            conn.commit()
            st.success("Selected students deleted successfully.")
    else:
        st.info("No students to display.")


def update_student(cursor, conn):
    st.header("Update Student")

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    if students:
        column_names = ["Serial No.", "ID", "Name", "Branch", "College", "Batch"]  # Define column titles with Serial No.
        df = pd.DataFrame(students, columns=["ID", "Name", "Branch", "College", "Batch"])  # Create DataFrame without Serial No.
        df.index = range(1, len(df) + 1)  # Start index from 1
        df.index.name = "Serial No."  # Set index name
        st.table(df)  # Display DataFrame as table
        selected_student = st.radio("Select Student to Update", df["ID"].tolist())  # Select student by ID
        if selected_student:
            cursor.execute("SELECT * FROM students WHERE id=?", (selected_student,))
            existing_data = cursor.fetchone()  # Fetch existing data for the selected student ID
            if existing_data:
                name = st.text_input("Updated Name", value=existing_data[1])
                branch = st.text_input("Updated Branch", value=existing_data[2])
                college = st.text_input("Updated College", value=existing_data[3])
                batch_options = ['None'] + get_batch_options(cursor)  # Add 'None' option
                selected_batches = st.multiselect("Updated Batches", batch_options, default=existing_data[4].split(", ") if existing_data[4] else [])  # Split the existing batches if they exist
                if st.button("Update Student"):
                    if name or branch or college:
                        updated_data = {
                            "name": name if name else existing_data[1],
                            "branch": branch if branch else existing_data[2],
                            "college": college if college else existing_data[3],
                            "batch": ", ".join(selected_batches) if selected_batches else None  # Join selected batches if they exist
                        }
                        cursor.execute("UPDATE students SET name=?, branch=?, college=?, batch=? WHERE id=?", (updated_data["name"], updated_data["branch"], updated_data["college"], updated_data["batch"], selected_student))
                        conn.commit()
                        st.success("Student updated successfully.")
                    else:
                        st.warning("Please input at least one field to update.")
            else:
                st.warning("Student not found.")
    else:
        st.info("No students to display.")


def display_students(cursor):
    st.header("Display Students")

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    if students:
        column_names = ["ID", "Name", "Branch", "College", "Batch"]  # Define column titles
        df = pd.DataFrame(students, columns=column_names)  # Create DataFrame with column names
        df.index = df.index + 1  # Shift index by 1 to start from 1
        st.table(df)  # Display DataFrame as table with index starting from 1
    else:
        st.info("No students to display.")


def add_batch(cursor, conn):
    st.header("Add Batch")
    batch_id = st.text_input("Batch ID")
    batch_name = st.text_input("Batch Name")
    if st.button("Add Batch"):
        if batch_id and batch_name:
            cursor.execute("SELECT * FROM batch WHERE id=?", (batch_id,))
            existing_batch_id = cursor.fetchone()
            if existing_batch_id:
                st.warning("Batch ID already exists.")
            else:
                cursor.execute("SELECT * FROM batch WHERE name=?", (batch_name,))
                existing_batch_name = cursor.fetchone()
                if existing_batch_name:
                    st.warning("Batch name already exists.")
                else:
                    cursor.execute("INSERT INTO batch (id, name) VALUES (?, ?)", (batch_id, batch_name))
                    conn.commit()
                    st.success("Batch added successfully.")
        else:
            st.warning("Please input both Batch ID and Batch Name.")


def display_batches(cursor):
    st.header("Display Batches")

    cursor.execute("SELECT id, name FROM batch")  # Select both batch ID and batch name
    batches = cursor.fetchall()

    if batches:
        column_names = ["Batch ID", "Batch Name"]  # Define column titles
        df = pd.DataFrame(batches, columns=column_names)  # Create DataFrame with column names
        df.index = df.index + 1  # Shift index by 1 to start from 1
        st.table(df)  # Display DataFrame as table with index starting from 1
    else:
        st.info("No batches to display.")


def delete_batch(cursor, conn):
    st.header("Delete Batch")

    cursor.execute("SELECT * FROM batch")
    batches = cursor.fetchall()

    if batches:
        column_names = ["Serial No.", "Batch Name"]  # Define column titles with Serial No.
        df = pd.DataFrame(batches, columns=["ID", "Batch Name"])  # Create DataFrame without Serial No.
        df.index = range(1, len(df) + 1)  # Start index from 1
        df.index.name = "Serial No."  # Set index name
        st.table(df)  # Display DataFrame as table
        selected_batches = st.multiselect("Select Batches to Delete", df["Batch Name"].tolist())  # Select batches by name
        if st.button("Delete Selected"):
            for batch_name in selected_batches:
                cursor.execute("DELETE FROM batch WHERE name=?", (batch_name,))
            conn.commit()
            st.success("Selected batches deleted successfully.")
    else:
        st.info("No batches to display.")


def create_students_table(cursor, conn):
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        branch TEXT NOT NULL,
                        college TEXT NOT NULL,
                        batch TEXT
                    )''')
    conn.commit()


def create_batch_table(cursor, conn):
    cursor.execute('''CREATE TABLE IF NOT EXISTS batch (
                        id VARCHAR PRIMARY KEY,
                        name TEXT NOT NULL
                    )''')
    conn.commit()


# Run the app
if __name__ == "__main__":
    main()
