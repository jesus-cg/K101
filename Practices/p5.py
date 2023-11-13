import psutil
from gpiozero import LED
from time import sleep

led={"red":LED(5),"yellow":LED(6),"green":LED(13)}

while True:
	for i in led.keys():
		led[i].blink(1,1)
		sleep(2)
		print(psutil.cpu_percent(interval = 1))
		print(psutil.cpu_count())


