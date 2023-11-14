import socket
from time import sleep

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ("0.0.0.0", 2345) #El puesto favorablemente debe ser mayor a 1024
print("Servidor en {} puerto {}".format(*server_address))
sock.bind(server_address)

sock.listen(1)

while True:
    print("waiting for a connection")
    connection, client_addres = sock.accept()
    try:
        print("connection from", client_addres)
        while True:
            data = connection.recv(16)
            print("received {!r}".format(data))
            if data:
                print("sending data back to the client")
                connection.sendall(data)
                if (data ==b"x"):
                    break
            else:
                print("mo data from", client_addres)
                break
    finally:
        print("Closing current connection")
        connection.close()