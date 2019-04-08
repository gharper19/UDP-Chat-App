import time
import socket
import sys

import threading
import socket

exitFlag = 0
class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, socket, sendmsg=False, reqUsers=False):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.sendmsg = sendmsg
        self.reqUsers = reqUsers
        self.socket = socket
    def run(self):
        x= 0
        print("%s activated!" % self.name)
        while x < 7: 
            try:
                
                run_client(self.name, self.socket)
                x += 1
            except Exception as e: 
                print("Error running client: %s" % e)
                break

def run_client(name, clientSocket): # <--- clientSocket not neccessary , use global socket
    # Take user input as text for message and send datagram to server socket
    msg = "Hey there Server! - from %s" % name
    try:
        clientSock.sendto(msg.encode('ascii'), (serverHost, serverPort))
        print("%s: Sent\n" % name )
    except Exception as e: 
        print("Error Sending Client Message")
        raise e

# Create GLOBAL Client Socket with SOCK_DGRAM to indicate use of UDP rather than Bytestream 
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Prepare request with Server Socket's Port and IP 
serverHost = '127.0.0.1'
serverPort = 9997
try: 
    clientSock.bind((serverHost, 9998))
except Exception as e: 
    print("Error binding Client socket")
    # raise e

# Create new threads
thread1 = myThread(1, "Thread-1", 1, clientSock)
thread2 = myThread(2, "Thread-2", 2, clientSock)

# Start new Threads
thread1.start()
thread2.start()

while 1: 
    msg = clientSock.recvfrom(1026)
    print(msg[0].decode('utf-8'))



## Client can send from two threads with same BINDED socket just fine as is, but throws an exception at some point after finishing for using same port
# can server recieve from both threads as a binded socket

### !!!! Okay i just looked and the clientSock obj is global and thats what is working in run_client not the clientSocket param i pass in
### So you cant pass sockets around but you CAN use same socket obj in two diff 