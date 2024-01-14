from time import sleep
import time, sys
import RPi.GPIO as GPIO
from datetime import datetime

import pymysql

DEBUG = False
dbserver = "192.168.1.252"
dbnamer = "Kestagua"
dbusername = "root"
dbpass = "1234"
INFLUX_ENABLE = 'yes'
sample_rate = 2 
m = 0.0021 

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
    print("Conexion con base de datos")
except pymysql.MySQLError as e:             #se agrego la conexion a base de datos
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

print("Water Flow - YF-S201 measurement")

while True:
    time_start = time.time();
    #today = datetime.date.today() #We need to identify today's date to differentiate it from tomorrow's. This would be yesterday
    init_time_start = time_start 
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
        
        #This helps to identify the first measurement - Chuy
        if i == 0:
            current_date_start = datetime.now().strf('%d')
        current__date = datetime.now().strf('%d')
        i += 1    
        try:
            with db_connection.cursor() as cursor:
                sql = "INSERT INTO Registros(DATETIME, db_hz, db_liter_by_min) VALUES('%s', %2.1f, %4.2f);" % (current_time, db_hz, db_liter_by_min)
                cursor.execute(sql)
            db_connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error al enviar a la base de datos: {e}")
            

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
        minutes = seconds/60,4
        print("\t", db_hz,'(hz) average')
        print('\t', db_liter_by_min,'(L/min)') 
        print(round(total_liters,4),"(L) today's total")
        print(round(minutes), '(min) total')
        print('-------------------------------------')

        #conditionals needed to post these values in the route named "registro" - Chuy
        #daily consumption
        if current_date_start == current__date:
            average_daily_consumption = total_liters/minutes
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
        elif len(listfif) > 15:
            listfif.remove(listfif[0])
            average_fifteen_consumption = sum(listfif)/fifmin

        #30 days consumption
        if len(listthi) == 30:
            average_thirty_consumption = sum(listthi)/thimin
        elif len(listfif) > 30:
            listthi.remove(listthi[0])
            average_thirty_consumption = sum(listthi)/thimin
        
        #60 days consumption
        if len(listsix) == 60:
            average_sixty_consumption = sum(listsix)/sixmin
        elif len(listsix) > 60:
            listsix.remove(listsix[0])
            average_sixty_consumption = sum(listsix)/sixmin
        
        json_body = [{
        "measurement": "temperature",
        "tags": {
            "serial": "WF-"+str(pin_input),
            "type": "WaterFlow"
        },
        "time": current_time,
        "fields": {
            "good_sample": float(db_good_sample),
            "hz": db_hz,
            "liter_by_min": db_liter_by_min
        }
        }]
  
    except KeyboardInterrupt:
        print('\n CTRL+C - Exiting')
        db_connection.close()
        GPIO.cleanup()
        sys.exit()
        
GPIO.cleanup()
db_connection.close()
print('Done')