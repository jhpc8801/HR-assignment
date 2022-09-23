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
employee_table = 'employee'
payroll_table = 'payroll'


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

# @app.route("/getEmpName", methods=['GET'])
# def GetEmpName():
#     emp_id = request.args['emp_id']

#     get_fn_sql = "SELECT first_name FROM " + employee_table + " WHERE emp_id" + " = " + emp_id
#     get_ln_sql = "SELECT last_name FROM " + employee_table + " WHERE emp_id" + " = " + emp_id

#     cursor1 = db_conn.cursor()
#     cursor2 = db_conn.cursor()
#     db_conn.commit()

#     if emp_id != "":
#         cursor1.execute(get_fn_sql)
#         cursor2.execute(get_ln_sql)
 
#         first_name = str(cursor1.fetchone()[0])
#         last_name = str(cursor2.fetchone()[0])

#     cursor1.close()
#     cursor2.close()

#     return render_template('EditPayroll.html', id=emp_id, fname=first_name, lname=last_name)

@app.route("/getEmpName", methods=['GET'])
def GetEmpName():
    emp_id = request.args['emp_id']

    get_fn_sql = "SELECT first_name FROM " + employee_table + " WHERE emp_id" + " = " + emp_id
    get_ln_sql = "SELECT last_name FROM " + employee_table + " WHERE emp_id" + " = " + emp_id
    get_stat_sql = "SELECT status FROM " + employee_table + " WHERE emp_id" + " = " + emp_id

    cursor1 = db_conn.cursor()
    cursor2 = db_conn.cursor()
    cursor3 = db_conn.cursor()
    db_conn.commit()

    if emp_id != "":
        cursor1.execute(get_fn_sql)
        cursor2.execute(get_ln_sql)
        cursor3.execute(get_stat_sql)
 
        first_name = str(cursor1.fetchone()[0])
        last_name = str(cursor2.fetchone()[0])
        status = str(cursor3.fetchone()[0])

    cursor1.close()
    cursor2.close()
    cursor3.close()

    return render_template('ManageAttendance.html', id=emp_id, fname=first_name, lname=last_name, stat=status)

@app.route("/attend", methods=['GET'])
def attendance():
    select_sql = "SELECT * FROM employee"
    cursor = db_conn.cursor()
    cursor.execute(select_sql)
    db_conn.commit()
    result = cursor.fetchall()

    arr = []
    for col in range(len(result)):
        arr.append([])
        arr[col].append(col + 1)
        arr[col].append(result[col][1] + result[col][2])
        arr[col].append(result[col][0])
        arr[col].append(result[col][8])
        arr[col].append(result[col][6])

    cursor.close()
 
    return render_template("Attendance.html", content=arr)

@app.route("/manageAtt", methods=['GET', 'POST'])
def manageAttendance():
    x = 0

    return render_template("ManageAttendance.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
