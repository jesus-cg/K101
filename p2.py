from gpiozero import LED, Button
button=Button(20)
Led1=LED(21)
while True:
	if button.is_pressed:
		Led1.on()
	else:
		Led1.off()
