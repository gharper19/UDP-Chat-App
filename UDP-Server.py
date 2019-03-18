import socket

# Create Server Socket with SOCK_DGRAM to indicate use of UDP rather than Bytestream 
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Assign hostname and port number, then bind to server socket
serverHost = "127.0.0.1"
serverPort = 9998
serverSock.bind((serverHost, serverPort))

# Keep Server Process running prepared to print client requests
print("Server Online... Waiting for Requests: \n")
while True:    
    clientData, clientAddr = serverSock.recvfrom(1024)
    print("From {}: {} ".format(str(clientAddr[0])+ ':' +str(clientAddr[1]), str(clientData)))

