
from flask import Flask, render_template, request
import boto3
import mysql.connector
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ---------- MYSQL CONNECTION ----------

conn = mysql.connector.connect(
    host="database-1.czumyw0wsosf.eu-north-1.rds.amazonaws.com",
    user="admin",
    password="manishanegi123",
    database="students_db"
)

cursor = conn.cursor()

# ---------- S3 CONNECTION ----------

s3 = boto3.client('s3')

BUCKET_NAME = "mn-data-bucket"

# ---------- HOME PAGE ----------

@app.route('/')
def home():
 cursor.execute("SELECT * FROM class_students")
 data = cursor.fetchall()
 return render_template("index.html", students=data)

# ---------- FORM SUBMIT ----------

@app.route('/upload', methods=['POST'])
def upload():

    name = request.form['name']
    age = request.form['age']
    email = request.form['email']

    image = request.files['image']
    import time
    filename = str(int(time.time())) + "_" + image.filename

    # Upload image to S3
    s3.upload_fileobj(
        image,
        BUCKET_NAME,
        filename
    )

    # Image URL
    image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"

    # Save data in RDS
    query = """
    INSERT INTO class_students(name, age, email, image_url)
    VALUES (%s, %s, %s, %s)
    """

    values = (name, age, email, image_url)

    cursor.execute(query, values)

    conn.commit()

    cursor.execute("SELECT * FROM class_students")
    data = cursor.fetchall()

    return render_template("index.html", students=data)

# ---------- RUN APP ----------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
