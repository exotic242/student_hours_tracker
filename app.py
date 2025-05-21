from flask import Flask, render_template, request, redirect, session
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace this with any random secret

# File paths
STUDENTS_FILE = 'shared/students.csv'

LOGS_FILE = 'shared/logs.csv'


# Ensure CSV files exist
if not os.path.exists(STUDENTS_FILE):
    with open(STUDENTS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['surname', 'name', 'email', 'password', 'grade', 'school', 'hours'])

if not os.path.exists(LOGS_FILE):
    with open(LOGS_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['email', 'date', 'time', 'activity', 'hours'])

@app.route("/")
def home():
    return render_template("home.html", logged_in=('email' in session))


# Register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        surname = request.form["surname"]
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        grade = request.form["grade"]
        school = request.form["school"]

        print("Saving student:", surname, name, email)

        with open(STUDENTS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([surname, name, email, password, grade, school, 0])

        return redirect("/login")
    return render_template("register.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with open(STUDENTS_FILE, newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row[2] == email and row[3] == password:
                    session['email'] = email
                    return redirect("/log-hours")
        error = "Invalid email or password."

    return render_template("login.html", error=error)

# Log Hours route
@app.route("/log-hours", methods=["GET", "POST"])
def log_hours():
    if 'email' not in session:
        return redirect("/login")

    if request.method == "POST":
        activity = request.form["activity"]
        hours = request.form["hours"]
        email = session["email"]
        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M")

                # Save to logs.csv
        with open(LOGS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([email, date, time, activity, hours])

        # Update total in students.csv
        students = []
        with open(STUDENTS_FILE, 'r', newline='') as f:
            reader = csv.reader(f)
            students = list(reader)

        for i, row in enumerate(students):
            if row[0] == "surname":
                continue  # skip header
            if row[2] == email:
                try:
                    old_hours = float(row[6])
                except:
                    old_hours = 0.0
                try:
                    new_hours = float(hours)
                except:
                    new_hours = 0.0
                students[i][6] = str(old_hours + new_hours)

        with open(STUDENTS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(students)


       

    return render_template("log_hours.html", success = True)

# My Hours route
@app.route("/my-hours")
def my_hours():
    if 'email' not in session:
        return redirect("/login")

    email = session['email']
    logs = []
    total_hours = 0.0

    with open(LOGS_FILE, newline='') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if row[0] == email:
                logs.append(row)
                try:
                    total_hours += float(row[4])
                except ValueError:
                    pass

    return render_template("my_hours.html", logs=logs, total=total_hours)

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
