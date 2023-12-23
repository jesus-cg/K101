
DEBUG = False
import time, sys
import RPi.GPIO as GPIO
from datetime import datetime
import pymysql

dbserver = "189.158.70.54"
dbnamer = "Kestagua"
dbusername = "root"
dbpass = "1234"
INFLUX_ENABLE = 'yes'

pin_input = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_input, GPIO.IN)

total_liters = 0
secondes = 0
sample_rate = 10  
time_start = 0
time_end = 0
period = 0;
hz = []      
m = 0.0021    
db_good_sample = 0
db_hz = 0
db_liter_by_min = 0

print("Water Flow - YF-S201 measurment")

while True:
    
    time_start = time.time();
    init_time_start = time_start 
    time_end = time_start + sample_rate
    hz = []
    sample_total_time = 0

    current = GPIO.input(pin_input)
    edge = current 

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

        secondes += sample_rate
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
        print("\t", db_hz,'(hz) average')
        print('\t', db_liter_by_min,'(L/min)') 
        print(round(total_liters,4),'(L) total')
        print(round(secondes/60,4), '(min) total')
        print('-------------------------------------')

        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
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
        GPIO.cleanup()
        sys.exit()
GPIO.cleanup()
print('Done')

