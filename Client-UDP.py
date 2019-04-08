import time
import socket
import sys
import random
import threading
import socket

exitFlag = 0
class ClientThread (threading.Thread):
    def __init__(self, threadID, name, counter, listenSocket):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.listenSocket = listenSocket
    def run(self):
        print("Starting %s" % self.name)
        wait_for_response(self.listenSocket)

'''

# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()

'''


################## Client Code ####################


msg_break = " /$MESSAGE_BREAK: "
stayOnServer = True
resp_wait= 1

name = ''
inbox=[]
ctrl_inbox = []

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
    clientSock.sendto(name.encode("ascii"), server)

    # Wait for userId and user list, then parse
    msg = clientSock.recvfrom(1026)[0]
    msg = msg.decode('utf-8')
   
    try:   
        name, userlist = msg.split(msg_break)
        print("connected..")
        print(userlist)
    except Exception as e: 
        print("Error Initiating with server." + str(e))
        raise e
    return clientSock, server


def wait_for_response(listenSocket):
    # Wait for messages from server     -    Issues with passing socket?
    global stayOnServer
    while stayOnServer:
        try:
            data = listenSocket.recvfrom(1026)[0].decode('utf-8')
            prefix, msg = clientData.split(msg_break)
            if "#./USER" in prefix:
                ctrl_inbox += [data]
            elif "#./EXIT" in prefix:
                stayOnServer = False
                # Close thread
            else: 
                inbox += [data]
                print(inbox)        # Issue printing while taking input
            
        except Exception as e:
            print("Error receiving messages from server %s: %s" % str(server) , e) 

def reqUserList():
    # Request User List with appended random number to determine most recent
    userlist=''
    check, check_inbox_limit= 0, 7
    print("Requesting updated user list ...")
    
    update_key = random.randint(1000, 9999)
    req = "#./USER" + msg_break + str(update_key)
    prefix ="#./USER" + str(update_key)
    try:
        clientSock.sendto(req.encode("ascii"), server)
    except Exception as e:
        print("Error requesting User list: %s")

    # Give receiver thread time to add to control inbox and check for response
    while check <= check_inbox_limit:
        time.sleep(resp_wait)
        for msg in ctrl_inbox:
            msg_prefix, userdata = msg.split(msg_break)
            if msg_prefix == prefix:
                return userdata
        if check == check_inbox_limit and userlist == '':
            return "Updated Userlist not found in inbox after waiting %d seconds %d" % (resp_wait, check_inbox_limit)
        check +=1  


def main_loop():
# Start thread to listen for server messages while also waiting for user input
    global stayOnServer
    listening_thread = ClientThread(threadID=1, name="Listening Thread", counter=1, listenSocket=clientSock)

    setDest = True
    debug_flag=1
    while stayOnServer: 
        ## Closed for debugging
        # if setDest:
        #     msg = input("Enter ./user to Select a user to message and ./exit to leave chat server. Enter ./inbox to view your message inbox.").strip()
        #     setDest= False
        # else:
        #     msg = input("Enter your message for " + dest + ". Enter ./user to change user and ./exit to leave chat server. Enter ./inbox to view your message inbox.").strip()
        # # Check for control commands
        if debug_flag:
            msg = './user'
            debug_flag= 0
        else: 
            return

        if msg == './user':
            # Get and print user list
            userlist = reqUserList()
            print(userlist)

            ## Include list of delimited clients as option for group messagse 
            dest = input("Enter the name of the user you want to message.").strip() # or is it split() ?
            print("Currently messaging %s" % dest)
        
        elif msg == './inbox': 
            print(inbox)
            '''
            print("Waiting on response ...")
            rcvMsg = s.recv(1024).decode()
            print(rcvMsg)
            break
            '''
        elif msg == './exit': 
            stayOnServer = False
            
        else: 
            if dest == name:
                print("Error, you entered your name as the recieving user")
                pass
            else:
                # Send user's message with destination user as message prefix 
                pkt = dest + msg_break + msg
                s.send(pkt.encode('ascii'), server)
                print("Sent!")

        # If issue with recv in both running threads just have seperate inbox for control and init msgs


    print("GoodBye!")


    input("Enter to close")


# Gets users name, initiates socket , and gets username and userlist from server    
clientSock, server = init_client()
main_loop()

# TODO: 
# Include user input for ports, server, name
# send server exit message to close the connection and remove user from active users list
   # -- Since client is always listening, can server just send out userlist when new user joins?
# see if printing incoming msgs while waiting on input is possible with
# After that: 
  # Allow users to select multiple destinations