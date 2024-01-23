from flask import Flask, render_template, flash, redirect, request, url_for
from forms import CrearCuenta, IniciarSesion
import regfflow
from regfflow import registart, flume, flumestop, showreg
import pymysql

app = Flask(__name__)

app.config['CLAVE_SECRETA'] = 'K101'

average_daily_consumption = regfflow.average_daily_consumption
average_fifteen_consumption = regfflow.average_fifteen_consumption
average_thirty_consumption = regfflow.average_thirty_consumption
average_sixty_consumption = regfflow.average_sixty_consumption

@app.route("/")
def welcome():
    return render_template("inicio.html")

@app.route("/crear-cuenta")
def ccacount():
    form =  CrearCuenta()
    return render_template("crear-cuenta.html", form = form)
    if form.validate_on_submit():
        flash(f"¡Cuenta creada para {form.username.data}!", "success")
        return redirect(url_for("welcome"))
     

@app.route("/login")
def isesion():
    form =  IniciarSesion()
    return render_template("login.html", form = form)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/registros")
def registros():
    return render_template("registro.html", average_daily_consumption = average_daily_consumption, average_fifteen_consumption = average_fifteen_consumption, average_thirty_consumption = average_thirty_consumption, average_sixty_consumption = average_sixty_consumption)

@app.route("/flujo", methods=["POST", "GET"])
def flujo():
    return render_template("flujo.html")
    if request.method == "POST":
        regfflow.flume()

@app.route("/base-de-registros")
def database():
    sql = "SELECT ID, DATETIME, db_hz, db_liter_by_min FROM Kegistros ORDER BY DATETIME ASC LIMIT 21600"
    result = regfflow.showreg(sql)
    return render_template("database.html", result = result)


if __name__== '__main__' :
    app.run(debug=True)
    #Whenever you need to use it with the Rasp, use:
    #app.run(debug=True, port=80, host="RPi")