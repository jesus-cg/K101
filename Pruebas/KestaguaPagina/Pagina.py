from flask import Flask, render_template
import regflow




app = Flask(__name__)

@app.route("/")
def welcome():
    return render_template("inicio.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/registros")
def registros():
    return render_template("registro.html")

if __name__== '__main__' :
    app.run(debug=True)