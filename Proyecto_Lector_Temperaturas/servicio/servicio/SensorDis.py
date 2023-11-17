from gpiozero import DistanceSensor
from time import sleep
import random
import pymysql
import datetime

ultrasonic = DistanceSensor(echo=17, trigger=4)
pin = 17
intervalo = 5
dbserver = "192.168.1.252" 
dbname = "proyecto1"
dbusername = "root"
dbpass = "1234"

print("cargando configuración")
f = open("config.txt","r") #requiere escribir toda la dirección del archivo

for i in f:
    val = i.split("=")
    if (val[0] == "pin"):
        pin = int(val[1])
    elif (val[0] == "intervalo"):
        intervalo == int(val[1])
    elif (val[0] == "dbname"):
        dbname == val[1]
    elif (val[0] == "dbusername"):
        dbusername == val[1]
    elif (val[0] == "dbpass"):
        dbpass == val[1]
    else:
        print("Error de configuación: ", val[0])

f.close()

db = pymysql.connect (host=dbserver, user=dbusername, password=dbpass,db=dbname, charset = "utf8")




print("Pin = ", pin)
print("intervalo = ", intervalo)

cur = db.cursor()
print("Iniciando")
while True:
    print("Leyendo información.")
    #humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin)
    #humedad = random.uniform(20.0,50.0)
    #temperatura = random.uniform(20.0,80.0)
    distancia=ultrasonic.distance
    if distancia is not None:
        sql = "INSERT INTO SensorDis VALUES ('%s', %4.2f, %4.2f);" % (datetime.datetime.now().strftime("%Y-%m-%d %H:$M:%S"), distancia)
        print(sql)
        cur.execute(sql)       
        db.commit()
    print("Distancia: ", distancia)
    sleep(5)

#db.close()
