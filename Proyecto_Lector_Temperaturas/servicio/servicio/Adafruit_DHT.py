import Adafruit_DHT
from time import sleep

sensor = Adafruit_DHT.DHT11
pin = 2

while True:
    humedad, temperatura = Adafruit_DHT.read_retry(sensor, pin)
    print("Humedad: ", humedad, "\nTemperatura: ", temperatura)
    sleep(5)