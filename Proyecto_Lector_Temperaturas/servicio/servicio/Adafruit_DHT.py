import Adafruit_DHT
from time import sleep
import random
import pymysql
import datetime

sensor = Adafruit_DHT.DHT11
pin = 17
intervalo = 5
dbserver = "192.168.68.115" #IP de MySQL
dbname = "proyecto1"
dbusername = "root"
dbpass = "1234"

print("cargando configuración")
f = open("config","r") #requiere escribir toda la dirección del archivo

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

db = pymysql.connect (host=dbserver, user=dbusername, password=dbpass,db=dbname, chartset = "utf8")




print("Pin = ", pin)
print("intervalo = ", intervalo)

cur = db.cursor()
print("Iniciando")
while True:
    print("Leyendo información.")
    humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin)
    #humedad = random.uniform(20.0,50.0)
    #temperatura = random.uniform(20.0,80.0)
    if humedad is not None and temperatura is not None:
        sql = "INSERT INTO temperaturas VALUES (%4.2f, %4.2f);" % (datetime.datetime.now().strftime("%Y-%m-%d %H:$M:%S"), temperatura)
        print(sql)
        cur.execute(sql)
        db.commit()
        db.close()
    print("Humedad: ", humedad, "\nTemperatura: ", temperatura)
    sleep(10)

db.close()