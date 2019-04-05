# Glenn Harper
import socket

# Create Client Socket with SOCK_DGRAM to indicate use of UDP rather than Bytestream 
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Prepare request with Server Socket's Port and IP 
serverHost = '127.0.0.1'
serverPort = 9997
clientSock.bind((serverHost, 9998))

# Take user input as text for message and send datagram to server socket
try:     
    clientSock.sendto(b"Greetings Server!", (serverHost, serverPort))
    print("Sending to server at %s" %serverHost)
except Exception as e:
    print("error %s" % e)
'''
try: 
    print(clientSock.recvfrom(1026))
except Exception as e: 
    print("Error with reciept: "+ str(e))
try:
    clientSock.sendto(
        input("Enter a message to send to send to the server:").encode('ascii'), 
        (serverHost, serverPort)
        )
except Exception as e:
    print(e)
try: print(clientSock.recvfrom(1026))
except Exception as e: 
    print(e)
'''
