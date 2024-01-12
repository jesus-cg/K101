from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def welcome():
    return "<h1>Welcome to Kestagua</h1>"

@app.route("/Registro")
def registro():
    return "<h1>Welcome to Kestagua</h1>"

if __name__== '__main__' :
    app.run(debug=True)