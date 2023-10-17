from gpiozero import LED, Button
from time import sleep
import random
LED1=LED(21)

button1=Button(20)
button2=Button(26)

while True:
	time = random.uniform(3,5)
	print("Listos")
	sleep(time)
	LED1.on()
	while True:
		if button1.is_pressed:
			print("Player 1 WINS")
			sleep(5)
		if button2.is_pressed:
			print("Player 2 WINS")
			sleep(5)
