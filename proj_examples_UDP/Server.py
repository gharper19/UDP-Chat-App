# Glenn Harper

import socket
import threading

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, clientAddr, clientData, task_flag=0 ):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.socket = socket
        self.clientAddr = clientAddr
        self.clientData = clientData
        self.task_flag= task_flag
    def run(self):
        x= 0
        print("Server's %s activated!\n" % self.name)
        try:    
            serverSock.sendto("Hey Client recv".encode('ascii'), self.clientAddr)
            print("Reply sent by sender thread")
        except Exception as e: 
            print("Error sending to client in %s at %s: %s " % (self.name, self.clientAddr, e))
        

# Create GLOBAL Server Socket with SOCK_DGRAM to indicate use of UDP rather than Bytestream 
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Assign hostname and port number, then bind to server socket
serverHost = "127.0.0.1"
serverPort = 9997
serverSock.bind((serverHost, serverPort))

# Keep Server Process running prepared to print client requests
print("Server Online... Waiting for Requests: \n")

while 1: 
    k=1
    data, addr =serverSock.recvfrom(1024)
    print(data.decode("utf-8"))
    newClientThread = myThread(1, "Thread-%d" %k, 1, addr, data) 
    newClientThread.start()

### REMEMBER: socket doesn't need to be binded to sendto so you can make a new socket if needed

# k+= 1
# listening_thread =  myThread(1, "Thread-%d" % k, 1, serverSock)



 
