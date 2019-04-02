import time
import socket
import sys

import threading
import socket

exitFlag = 0
class ClientThread (threading.Thread):
    def __init__(self, threadID, name, counter, sendmsg=False, requestUsers=False):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        # Call methods here
        pass 

'''
# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()

'''


################## Client Code ####################

def init_client():
    # Init and bind client socket
    clientHost = '127.0.0.1'
    clientPort = 9998
    clientSock =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.bind((clientHost, clientPort)) 
    
    # Get Server IP and port
    host = '127.0.0.1'   #'192.168.56.1'#input(str("Please enter the server address : "))#
    port = 9997 # Or should it be 1024 (server rcv-from port?) 
    server = (host,port)

    # Get username
    name = "client_tester_guy"

    # Initialize Client as active with server
    print("trying to connect to Server at ", host , ":", port)
    # time.sleep(1)
    try: 
        clientSock.sendto(name.encode("ascii"), server)

        # Wait for userId and user list, then parse
        msg = clientSock.recvfrom(1026)[0]
        msg.decode('utf-8')
        userName, userlist = msg.split(" /$MESSAGE_BREAK: ")
        print("connected..")
        print(userlist)
    except Exception as e: 
        print("Error Initiating with server." + str(e))
        raise e
    return clientSock, server

    


def wait_for_resp():
    # ! decode msgs into utf-8 ? and use bytes() ?
    # try catch with limit on server responses
    pass

def send_message(rcv_user):
    pass


def main_loop():
    # Gets users name, initiates socket , and gets username and userlist from server    
    socket, server = init_client()

    stayOnServer = True
    while stayOnServer: 
        # Get user's destination and message data
        dest = str(input("Select a user to message.")) # use .ignoreCase() or make users and dest UPPERCASE for comparison; 
        
        keepCurrentDest = True
        while keepCurrentDest:
            msg = input("Enter your message for " + dest + ". Enter ./user to change user and ./exit to leave chat server. Enter ./wait to wait for messages.")
            
            # Check for control commands
            if msg == './user':
                keepCurrentDest = False
                break
            elif msg == './exit': 
                stayOnServer = False
                break
            elif msg == './wait': 
                pass
                '''
                print("Waiting on response ...")
                rcvMsg = s.recv(1024).decode()
                print(rcvMsg)
                break
                '''
            else: 
                # Send message -  Will eventually need user input to determine if currently wanting to send or check for recieved messages(inbox) 
                pkt = dest + ' /$MESSAGE_BREAK: ' + msg
                s.send(pkt.encode('ascii'), server)
                print("Sent!")

                '''
                # recieve messages from server
                print("Waiting on response ...")
                rcvMsg = s.recv(1024).decode()
                print(rcvMsg)
                '''

    print("GoodBye!")


    input("Enter to close")

main_loop()