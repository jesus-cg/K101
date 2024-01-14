from flask import Flask
import mariadb
app = Flask(__name__)
conn = mariadb.connect(
         host='127.0.0.1', #RPi IP
         port= 3306,
         user='root',
         password='goldSTAR',
         database='movieDb')
cur = conn.cursor()
@app.route("/index")
def index():
    return "Connected to database"
if __name__ == "__main__":
    app.run()