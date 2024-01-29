from flask import Flask, render_template, flash, redirect, request, url_for
from forms import CrearCuenta, IniciarSesion
from time import sleep
import time, sys
import RPi.GPIO as GPIO
from datetime import datetime
#import regfflow
#from regfflow import registart, avgd, avgfif, avgthi, avgsix, flume, flumestop, showreg
import pymysql

app = Flask(__name__)

app.config['CLAVE_SECRETA'] = 'K101'

'''
average_daily_consumption = avgd.average_daily_consumption
average_fifteen_consumption = avgfif.average_fifteen_consumption
average_thirty_consumption = avgthi.average_thirty_consumption
average_sixty_consumption = avgsix.average_sixty_consumption
'''

@app.route("/")
def welcome():
    '''
    dbserver = "172.32.180.247"
    dbnamer = "Kestagua"
    dbusername = "root"
    dbpass = "1234"

    DEBUG = False
    INFLUX_ENABLE = 'yes'
    sample_rate = 2 
    m = 0.0021
    ID = 1234 #de prueba

    try:
        db_connection=pymysql.connect(host=dbserver,user=dbusername,passwd=dbpass,db=dbnamer)
        print("Conexion con la base de datos")
    except pymysql.MySQLError as e:             #se agregó la conexion a base de datos
        print(f"Error al conectar: {e}")
        sys.exit(1) 

    
    pin_input = 8
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_input, GPIO.IN)

    total_liters = 0
    seconds = 0
    time_start = 0
    time_end = 0
    period = 0;
    hz = []      
    db_good_sample = 0
    db_hz = 0
    db_liter_by_min = 0
    daily_db_liter_by_min = 0

    #cur = db_connection.cursor()

    print("Flujo de Agua - Detección con el sensor YF-S201")


    while True:
        time_start = time.time(); 
        time_end = time_start + sample_rate
        hz = []
        sample_total_time = 0

        current = GPIO.input(pin_input)
        edge = current 

        #Connection with the Flowmeter and the assignment of values to each variable.
        try:
            while time.time() <= time_end:
                t = time.time();
                v = GPIO.input(pin_input)
                if current != v and current == edge:
                    period = t - time_start 
                    new_hz = 1/period
                    hz.append(new_hz)              
                    sample_total_time += t - time_start
                    time_start = t;
                
                    if DEBUG:
                        print(round(new_hz, 4))     
                        sys.stdout.flush()
                current = v;

            #Our way to certify that the code is working :>
            print('-------------------------------------')
            print('Current Time:',time.asctime(time.localtime()))
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            seconds += sample_rate
            nb_samples = len(hz);
            if nb_samples >0:
                average = sum(hz) / float(len(hz));

                good_sample = sample_total_time/sample_rate
                print("\t", round(sample_total_time,4),'(sec) good sample')
                db_good_sample = round(good_sample*100,4)
                print("\t", db_good_sample,'(%) good sample')
                average = average * good_sample
            else:
                average = 0
            average_liters = average*m*sample_rate;
            total_liters += average_liters
            db_hz = round(average,4);
            daily_db_liter_by_min = round(total_liters*(60/seconds),4)
            db_liter_by_min= round(average_liters*(60/sample_rate),4)
            
            print("\t", db_hz,'(hz) average')
            print('\t', db_liter_by_min,'(L/min)') 
            print(round(total_liters,4),"(L) today's total")
            print('-------------------------------------')
            try:
                with db_connection.cursor() as cursor:
                    sql = "INSERT INTO Kegistros(ID, TIEMPO, LITMIN, LITCONS) VALUES('%i', '%s', '%4.2f', '%6.2f' );"
                    data = (int(ID), current_time, db_liter_by_min, daily_db_liter_by_min)
                    cursor.execute(sql, data)
                db_connection.commit()
            except pymysql.MySQLError as e:
                print(f"Error al enviar a la base de datos: {e}")
            
            try:
                with db_connection.cursor() as cursor:
                    sql = "SELECT AVG(LITMIN) FROM Kegistros WHERE TIEMPO >= CURDATE() and TIEMPO < (CURDATE()+1)"
                    cursor.execute(sql)
                    cons= cursor.fetchall()
                    dato1 = cons[0][0]
                    average_daily_consumption = dato1
                    #db_connection.commit()
                    return average_daily_consumption
            except pymysql.MySQLError as e:
                print(f"Error al consultar los datos: {e}")
        except KeyboardInterrupt:
            print('\n CTRL+C - Exiting')
            db_connection.close()
            GPIO.cleanup()
            sys.exit()

    GPIO.cleanup()
    db_connection.close()
    print('Done')
    '''
    return render_template("inicio.html")
    
@app.route("/crear-cuenta")
def ccacount():
    #form =  CrearCuenta()
    return render_template("crear-cuenta.html") #, form = form
   # if form.validate_on_submit():
    #    flash(f"¡Cuenta creada para {form.username.data}!", "success")
     #   return redirect(url_for("welcome"))
     

@app.route("/login")
def isesion():
    #form =  IniciarSesion()
    return render_template("login.html") #, form = form

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/registros")
def registros():
    return render_template("registro.html")
                           #, average_daily_consumption = average_daily_consumption, average_fifteen_consumption = average_fifteen_consumption, average_thirty_consumption = average_thirty_consumption, average_sixty_consumption = average_sixty_consumption)

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