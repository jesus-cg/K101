import socket
from time import sleep

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("RASPBERRY", 2345) #El puesto favorablemente debe ser mayor a 1024
print("Conectando a {} puerto {}".format(*server_address))
sock.connect(server_address)

try:
    message = "mensaje muy largo"
    print("sending {!r}".format(message))
    sock.sendall(message)

    amount_received = 0
    amount_expected = len(message)

    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print("received {!r}".format(data))

finally:
    print("closing socket")
    sock.close()