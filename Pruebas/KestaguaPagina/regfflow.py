from time import sleep
import time, sys
import RPi.GPIO as GPIO
from datetime import datetime

import pymysql

#import other codes
import forms
import Pagina

'''
def gendatabase(): #Generamos una database para cada usuario :3
    DEBUG = False
    dbserver = "192.168.1.252"
    dbnamer = "Kestagua"
    dbusername = "root"
    dbpass = "1234"
    INFLUX_ENABLE = 'yes'

    username = Pagina.ccacount.username

    try:
        db_connection=pymysql.connect(host=dbserver,user=dbusername,passwd=dbpass,db=dbnamer)
        print("Conexion con la base de datos")
    except pymysql.MySQLError as e:             #se agregó la conexion a base de datos ;P
        print(f"Error al conectar: {e}")
        sys.exit(1) 
    try:
        with db_connection.cursor() as cursor:
            #Crea una base de datos para el registro continuo :o
            sql = "INSERT INTO Kestagua(P)DB_", username, " AS SELECT (DATETIME,db_hz,db_liter_by_min) FROM Registros"
            cursor.execute(sql)
            #Crea una base de datos para los flujos que quieran hacer ;>
            #lqs = "CREATE TABLE Kestagua(F)DB_", username, " (REGISTRO INT(100000),TIEMPO TOTAL TIME(100000),db_liter_by_min FLOAT(p))"
            #Sale mejor crear una template y copiarla con la siguiente línea de código:
            #lqs = "CREATE TABLE Kestagua(P)DB_", username, " AS SELECT (REGISTRO,TIEMPO TOTAL,db_liter_by_min) FROM Flujos"
            #cursor.execute(lqs)

        db_connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear la base de datos: {e}")
'''


def registart(): #Needed to be able to use it in our webpage
    DEBUG = False
    db_connection = None
    dbserver = "192.168.1.252"
    dbnamer = "Kestagua"
    dbusername = "root"
    dbpass = "1234"
    INFLUX_ENABLE = 'yes'
    sample_rate = 2 
    m = 0.0021
    ID = 1234 #de prueba

    #Defining some variables
    average_daily_consumption = 0
    average_fifteen_consumption = 0
    average_thirty_consumption = 0
    average_sixty_consumption = 0    
    
    #Lists
    listfif = []
    listthi = []
    listsix = []

    #Counter variables
    i = 0

    #Constants
    fifmin = 21600
    thimin = 43200
    sixmin = 86400

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

            print('-------------------------------------')
            print('Current Time:',time.asctime(time.localtime()))
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            #This helps to identify the first measurement - Chuy ;P
            if i == 0:
                current_date_start = datetime.now().strf('%d')
            current__date = datetime.now().strf('%d')
            i += 1    

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
            db_liter_by_min= round(average_liters*(60/sample_rate),4)
            minutes = seconds/60
            print("\t", db_hz,'(hz) average')
            print('\t', db_liter_by_min,'(L/min)') 
            print(round(total_liters,4),"(L) today's total")
            print(round(minutes), '(min) total')
            print('-------------------------------------')

            #conditionals needed to post these values in the route named "registro" - Chuy
            #daily consumption
            if current_date_start == current__date:
                average_daily_consumption = total_liters/minutes
                return average_daily_consumption
            else:
                average_daily_consumption = 0
                total_liters = 0
                seconds = 0
                i = 0
                listfif.append(total_liters) #list of daily consumption
                listthi.append(total_liters) #list of daily consumption
                listsix.append(total_liters) #list of daily consumption
            
            #15 days consumption
            if len(listfif) == 15:
                average_fifteen_consumption = sum(listfif)/fifmin
                return average_fifteen_consumption
            elif len(listfif) > 15:
                listfif.remove(listfif[0])
                average_fifteen_consumption = sum(listfif)/fifmin
                return average_fifteen_consumption

            #30 days consumption
            if len(listthi) == 30:
                average_thirty_consumption = sum(listthi)/thimin
                return average_thirty_consumption
            elif len(listfif) > 30:
                listthi.remove(listthi[0])
                average_thirty_consumption = sum(listthi)/thimin
                return average_thirty_consumption
                        
            #60 days consumption
            if len(listsix) == 60:
                average_sixty_consumption = sum(listsix)/sixmin
                return average_sixty_consumption
            elif len(listsix) > 60:
                listsix.remove(listsix[0])
                average_sixty_consumption = sum(listsix)/sixmin
                return average_sixty_consumption
            
            try:
                with db_connection.cursor() as cursor:
                    sql = "INSERT INTO Kegistros(ID, DATETIME, db_hz, db_liter_by_min) VALUES('%i, '%s', %2.1f, %4.2f);" % (ID,current_time, db_hz, db_liter_by_min)
                    cursor.execute(sql)
                db_connection.commit()
            except pymysql.MySQLError as e:
                print(f"Error al enviar a la base de datos: {e}")
            
        except KeyboardInterrupt:
            print('\n CTRL+C - Exiting')
            db_connection.close()
            GPIO.cleanup()
            sys.exit()
        
    GPIO.cleanup()
    db_connection.close()
    print('Done')

def showreg(query):
    DEBUG = False
    db_connection = None
    cur = None  
    dbserver = "192.168.1.252"
    dbnamer = "Kestagua"
    dbusername = "root"
    dbpass = "1234"
    charst = 'utf8'
    INFLUX_ENABLE = 'yes'
    sample_rate = 2 
    m = 0.0021
    ID = 1234 #de prueba
    
    try:
        db_connection=pymysql.connect(host=dbserver,user=dbusername,passwd=dbpass,db=dbnamer, charset=charst)
        print("Conexion con la base de datos")
    except pymysql.MySQLError as e:             #se agregó la conexion a base de datos
        print(f"Error al conectar: {e}")
        sys.exit(1)
    


    try:
        cur = db_connection.cursor()
        cur.execute(query)
        result = cur.fetchall()
        db_connection.close()
        return result
    except pymysql.MySQLError as e:
        print(f"Error al crear la base de datos: {e}")
    




def flume(): #registramos los flujos del usuario
    DEBUG = False
    db_connection = None
    dbserver = "192.168.1.252"
    dbnamer = "Kestagua"
    dbusername = "root"
    dbpass = "1234"
    INFLUX_ENABLE = 'yes'
    sample_rate = 2 
    m = 0.0021 
    ID = 1234 #Prueba

    try:
        db_connection=pymysql.connect(host=dbserver,user=dbusername,passwd=dbpass,db=dbnamer)
        print("Conexion con la base de datos")
    except pymysql.MySQLError as e:             #se agregó la conexion a base de datos ;P
        print(f"Error al conectar: {e}")
        sys.exit(1) 
    
    pin_input = 8
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin_input, GPIO.IN)

    time_start = 0
    time_end = 0
    hz = []      
    db_good_sample = 0
    db_hz = 0
    db_liter_by_min = 0
    i = 0

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

            if i == 0:
                current_time_start = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            current__time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            i += 1

            print('-------------------------------------')
            print('Start:',time.asctime(time.localtime()))
            
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
            db_liter_by_min= round(average_liters*(60/sample_rate),4)
        except KeyboardInterrupt:
            print('\n CTRL+C - Exiting')
            db_connection.close()
            GPIO.cleanup()
            sys.exit()

def flumestop(current_time, current_time_start, db_liter_by_min):
    DEBUG = False
    db_connection = None
    dbserver = "192.168.1.252"
    dbnamer = "Kestagua"
    dbusername = "root"
    dbpass = "1234"
    INFLUX_ENABLE = 'yes'
    ID = 1234 #de prueba
    regname = "Registro N.#"


    try:
        db_connection=pymysql.connect(host=dbserver,user=dbusername,passwd=dbpass,db=dbnamer)
        print("Conexion con la base de datos")
    except pymysql.MySQLError as e:             #se agregó la conexion a base de datos ;P
        print(f"Error al conectar: {e}")
        sys.exit(1) 


    date_format = "%d/%m/%Y %H:%M:%S"

    start = datetime.strptime(current_time_start, date_format)
    end = datetime.strptime(current_time, date_format)

    time_difference = end - start
    time_difference_in_hours = time_difference.total_seconds() / 3600


    try:
        with db_connection.cursor() as cursor:
            sql = "INSERT INTO Flugua (ID, REGISTRO,TIEMPO TOTAL,db_liter_by_min) VALUES('%i','%s', '%s', %4.2f);" % (ID, regname, time_difference_in_hours, db_liter_by_min)
            cursor.execute(sql)
        db_connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error al crear la base de datos: {e}")