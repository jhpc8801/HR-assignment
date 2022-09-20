from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import webbrowser
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/manageAtt", methods=['GET', 'POST'])
def manageAttendance():
    select_sql = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(select_sql)
    db_conn.commit()
    result = cursor.fetchall()

    p = []      # for creating a whole new html page using string

    # later one by one append the html code together with the data to the string

    for row in result:          # row[] could be the data in the mySQL database
        number = "<tr><td>1. </td>" #"<tr><td>%s</td>"%row[0]
        p.append(number)
        name = "<td>%s</td>"%(row[1] + row[2])
        p.append(name)
        empID = "<td>%s</td>"%row[0]
        p.append(empID)
        date = "<td>%s</td>"%row[8]
        p.append(date)
        status = "<td>%s</td>"%row[6]
        p.append(status)
        if (row[7] == "checked"):
            attend = '''<td><input type="checkbox" class="empAttend" name="emp_attendance" value="attend" checked></td></tr>'''
        else:
            attend = '''<td><input type="checkbox" class="empAttend" name="emp_attendance" value="attend"></td></tr>'''
        p.append(attend)

    contents = '''<!DOCTYPE html>
<html>
<head>
    <title>Manage Attendance for Employees</title>'''

    style = '''
    {% load static %}
    <link rel='stylesheet' href="{% static 'ManageAttendance.css' %}">'''

    contents.append(style)

    contents2 = '''
</head>
<body>
    <h1>Attendance Management</h1>
    <button>Back</button>

    <table>
        <tr>
          <th>No.</th>
          <th>Employee Name</th>
          <th>Emp ID</th>
          <th>Date modified</th>
          <th>Status</th>
          <th>Attendance</th>
        </tr>
    %s
    </table>
</body>
</html>'''%(p)

    contents.append(contents2)


    # surround the %s with html file code that previously designed

    filename = 'ManageAttendance.html'

    def main(contents, filename):
        output = open(filename,"w")
        output.write(contents)
        output.close()

    cursor.close()

    main(contents, filename)    
    # webbrowser.open(filename)

    #cursor.close()
    # if(db_conn.is_connected()):
    #     cursor.close()
    #     db_conn.close()
    #     print("MySQL connection is closed.")   
    return render_template(contents)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
