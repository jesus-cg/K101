from flask import Flask, render_template
import os
import pymysql

app=Flask(__name__)

@app.route("/method_get", methods=["GET"])
def index():
    return render_template("html_test.html")
@app.route("/sub1")
def sub1():
    return "SUB1 Page"

@app.route("/reporte", methods="POST")
def reporte():
    resultado = ObtenTemperaturas();
    return render_template("reporte.html", res = resultado)

@app.route("/configuración")
def configuración():
    return render_template("configuracion.html")

@app.route("/grabardatos", methods ="POST")
def grabardatos():
    f = open("config","r") #requiere escribir toda la dirección
    f.close()

if __name__ == "__main__":
    app.run(debug=True,port=80,host="0.0.0.0")