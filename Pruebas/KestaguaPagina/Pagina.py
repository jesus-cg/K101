from flask import Flask, render_template
from forms import CrearCuenta, IniciarSesion
#import regfflow

app = Flask(__name__)

app.config['CLAVE_SECRETA'] = 'K101'

average_daily_consumption = 0
average_fifteen_consumption = 0
average_thirty_consumption = 0
average_sixty_consumption = 0

@app.route("/")
def welcome():
    return render_template("inicio.html")

@app.route("/create-account")
def ccacount():
    form =  CrearCuenta()
    #return render_template("create_account.html", form = form)

@app.route("/login")
def isesion():
    form =  IniciarSesion()
    #return render_template("login.html", form = form)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/registros")
def registros():
    return render_template("registro.html", average_daily_consumption = average_daily_consumption, average_fifteen_consumption = average_fifteen_consumption, average_thirty_consumption = average_thirty_consumption, average_sixty_consumption = average_sixty_consumption)

if __name__== '__main__' :
    app.run(debug=True)