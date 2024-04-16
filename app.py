from flask import Flask, render_template, request
from pymysql import connections
import os
import random
import argparse

app = Flask(__name__)

DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
COLOR_FROM_ENV = os.environ.get('APP_COLOR') or "lime"
DBPORT = int(os.environ.get("DBPORT", 3306))  # Default MySQL port is 3306
IMAGE_URL = os.environ.get("IMAGE_URL") or ""
GROUP_NAME = os.environ.get("GROUP_NAME") or "Mike and Prason (Duo)"
SLOGAN = os.environ.get("SLOGAN") or "CLO835 Employee DBMS by MP"

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)
output = {}
table = 'employee'

# Define the supported color codes
color_codes = {
    "red": "#e74c3c",
    "green": "#16a085",
    "blue": "#89CFF0",
    "blue2": "#30336b",
    "pink": "#f4c2c2",
    "darkblue": "#130f40",
    "lime": "#C1FF9C",
}

# Create a string of supported colors
SUPPORTED_COLORS = ",".join(color_codes.keys())

# Generate a random color
COLOR = random.choice(["red", "green", "blue", "blue2", "darkblue", "pink", "lime"])


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('addemp.html', color=IMAGE_URL, head=GROUP_NAME, slogan=SLOGAN)


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', color=IMAGE_URL, head=GROUP_NAME, slogan=SLOGAN)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"

    finally:
        cursor.close()


    print("all modification done...")
    return render_template('addempoutput.html', name=emp_name, color=IMAGE_URL, head=GROUP_NAME, slogan=SLOGAN)



@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", color=IMAGE_URL, head=GROUP_NAME, slogan=SLOGAN)


@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()

        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
        else:
            return "No employee found."

    except Exception as e:
        print(e)

    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output["emp_id"], fname=output["first_name"],
                           lname=output["last_name"], interest=output["primary_skills"], location=output["location"], color=IMAGE_URL, head=GROUP_NAME, slogan=SLOGAN)


if __name__ == '__main__':
    # Check for Command Line Parameters for color
    parser = argparse.ArgumentParser()
    parser.add_argument('--color', required=False)
    args = parser.parse_args()

    if args.color:
        print("Color from command line argument =", args.color)
        COLOR = args.color
        if COLOR_FROM_ENV:
            print(f"A color was set through environment variable - {COLOR_FROM_ENV}. However, color from the command line argument takes precedence.")
    elif IMAGE_URL:
        print("Getting Background Image using URL =", IMAGE_URL)
        COLOR = IMAGE_URL
    else:
        print("No command line argument or environment variable. Picking a Random Color =", COLOR)

    # Check if the input color is a supported one
    if COLOR not in color_codes:
        print("Color not supported. Received '" + COLOR + "' expected one of " + SUPPORTED_COLORS)
        exit(1)

    app.run(host='0.0.0.0', port=81, debug=True)
