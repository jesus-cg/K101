from gpiozero import DistanceSensor
from flask import Flask,request, render_template
import pymysql

db = None
cur = None
app = Flask(__name__)

def select(query):
    db = pymysql.connect(host='192.168.1.252', user='root', password='1234', db='proyecto1', charset='utf8')
    cur = db.cursor()
    cur.execute(query)
    result = cur.fetchall()
    db.close()
    return result

@app.route('/SensorDis')
def lm23_chart():
    sql = "SELECT distancia, fecha FROM SensorDis ORDER BY fecha ASC LIMIT 100"
    result = select(sql)
    return render_template("SensorDis.html", result=result)

if __name__ == '__main__':
    app.run(debug=True, port=80, host='192.168.1.252')

