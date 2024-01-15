from flask import Flask, render_template, flash, redirect, url_for
from forms import CrearCuenta, IniciarSesion
##import regfflow
#from regfflow import registart

app = Flask(__name__)

app.config['CLAVE_SECRETA'] = 'K101'

#average_daily_consumption = regfflow.average_daily_consumption
#average_fifteen_consumption = regfflow.average_fifteen_consumption
#average_thirty_consumption = regfflow.average_thirty_consumption
#average_sixty_consumption = regfflow.average_sixty_consumption

@app.route("/")
def welcome():
    return render_template("inicio.html")

@app.route("/create-account")
def ccacount():
    form =  CrearCuenta()
    if form.validate_on_submit():
        #flash(f"¡Cuenta creada para {form.username.data}!", "success")
        return redirect(url_for("welcome"))
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