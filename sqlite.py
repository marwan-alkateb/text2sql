import sqlite3

## connect to sqllite
connection = sqlite3.connect("student.db")

##create a cursor object to insert record,create table
cursor = connection.cursor()

## Create and populate the tables

# Houses table
cursor.execute("""DROP TABLE IF EXISTS houses""")
cursor.execute("""
    CREATE TABLE houses (
        house_id INTEGER PRIMARY KEY,
        house_name VARCHAR(50),
        head_of_house VARCHAR(50)
    )
""")
cursor.execute('''INSERT INTO houses (house_name, head_of_house) VALUES ('Gryffindor', 'Minerva McGonagall')''')
cursor.execute('''INSERT INTO houses (house_name, head_of_house) VALUES ('Hufflepuff', 'Pomona Sprout')''')
cursor.execute('''INSERT INTO houses (house_name, head_of_house) VALUES ('Ravenclaw', 'Filius Flitwick')''')
cursor.execute('''INSERT INTO houses (house_name, head_of_house) VALUES ('Slytherin', 'Severus Snape')''')

# Students table
cursor.execute("""DROP TABLE IF EXISTS students""")
cursor.execute("""
    CREATE TABLE students (
        student_id INTEGER PRIMARY KEY,
        name VARCHAR(50),
        house_id INTEGER,
        year INTEGER,
        FOREIGN KEY (house_id) REFERENCES houses(house_id)
    )
""")
cursor.execute('''INSERT INTO students (name, house_id, year) VALUES ('Harry Potter', 1, 5)''')
cursor.execute('''INSERT INTO students (name, house_id, year) VALUES ('Hermione Granger', 1, 5)''')
cursor.execute('''INSERT INTO students (name, house_id, year) VALUES ('Ron Weasley', 1, 5)''')
cursor.execute('''INSERT INTO students (name, house_id, year) VALUES ('Draco Malfoy', 4, 5)''')
cursor.execute('''INSERT INTO students (name, house_id, year) VALUES ('Luna Lovegood', 3, 5)''')

# Courses table
cursor.execute("""DROP TABLE IF EXISTS courses""")
cursor.execute("""
    CREATE TABLE courses (
        course_id INTEGER PRIMARY KEY,
        course_name VARCHAR(50),
        instructor_id INTEGER,
        FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
    )
""")
cursor.execute('''INSERT INTO courses (course_name, instructor_id) VALUES ('Defense Against the Dark Arts', 1)''')
cursor.execute('''INSERT INTO courses (course_name, instructor_id) VALUES ('Potions', 2)''')
cursor.execute('''INSERT INTO courses (course_name, instructor_id) VALUES ('Herbology', 3)''')
cursor.execute('''INSERT INTO courses (course_name, instructor_id) VALUES ('Transfiguration', 4)''')
cursor.execute('''INSERT INTO courses (course_name, instructor_id) VALUES ('Charms', 5)''')

# Enrollments table
cursor.execute("""DROP TABLE IF EXISTS enrollments""")
cursor.execute("""
    CREATE TABLE enrollments (
        enrollment_id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        enrollment_date DATE,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    )
""")
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (1, 1, '2023-01-15')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (2, 1, '2023-01-15')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (3, 1, '2023-01-15')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (4, 1, '2023-01-15')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (5, 1, '2023-01-15')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (1, 2, '2023-01-16')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (4, 2, '2023-01-16')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (2, 3, '2023-01-17')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (5, 3, '2023-01-17')''')
cursor.execute('''INSERT INTO enrollments (student_id, course_id, enrollment_date) VALUES (3, 4, '2023-01-18')''')

# Instructors table
cursor.execute("""DROP TABLE IF EXISTS instructors""")
cursor.execute("""
    CREATE TABLE instructors (
        instructor_id INTEGER PRIMARY KEY,
        name VARCHAR(50),
        course_id INTEGER,
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    )
""")
cursor.execute('''INSERT INTO instructors (name, course_id) VALUES ('Remus Lupin', 1)''')
cursor.execute('''INSERT INTO instructors (name, course_id) VALUES ('Severus Snape', 2)''')
cursor.execute('''INSERT INTO instructors (name, course_id) VALUES ('Pomona Sprout', 3)''')
cursor.execute('''INSERT INTO instructors (name, course_id) VALUES ('Minerva McGonagall', 4)''')
cursor.execute('''INSERT INTO instructors (name, course_id) VALUES ('Filius Flitwick', 5)''')

## Display all the records
print("The inserted students are")
data = cursor.execute('''Select * from students''')
for row in data:
    print(row)

## Commit your changes in the database
connection.commit()
connection.close()
