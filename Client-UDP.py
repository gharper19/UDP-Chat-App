import time
import socket
import sys
import random
import threading
import socket

exitFlag = 0
class ClientThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    
    def run(self):
        global stayOnServer
        global inbox
        global ctrl_inbox

        # Listening loop waiting for messages from the Server  
        while stayOnServer:
            prefix = ''
            data = ''
            try:
                clientData = clientSock.recvfrom(1026)[0].decode('utf-8')
                
                # Acquire thread lock to assure this runs with main thread
                threadLock.acquire()

                # Check for message break and seperate tokens
                if msg_break in clientData:
                    prefix, data = clientData.split(msg_break)
                else:
                    data = clientData
                
                # Check message for control responses
                if "#./USER" in prefix:
                    ctrl_inbox += [clientData]
                    print("[INFO] CTRL Inbox: " + str(ctrl_inbox))
                elif "#./EXIT" in prefix:
                    stayOnServer = False
                elif "#./ERROR_INVALID_USER" in prefix:
                    ctrl_inbox += [clientData]
                    print("Recent message '%s' failed to send. Destination user was not found in active userlist."
                        % data)
                else: 
                    inbox += [data]
                    time.sleep(2)
                    print("[INFO] MSG Inbox: " + str(inbox))        
                
                threadLock.release()
            except Exception as e:
                print("Error receiving messages from server %s: %s" % (str(server) , e))

################## Client Code ####################


msg_break = " /$MESSAGE_BREAK: "
stayOnServer = True
streamInbox= False
resp_wait= 1

name = ''
inbox=[]
ctrl_inbox = []


def init_client():
# Get user data for establishing connection and request username and userlist from server 
    
    # Init and bind client socket
    clientHost = '127.0.0.1'
    clientPort = 9998
    clientSock =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSock.bind((clientHost, clientPort)) 
    
    # Get Server IP and port
    host = '127.0.0.1'   #'192.168.56.1'#input(str("Please enter the server address : "))#
    port = 9997
    server = (host,port)

    # Get username
    name = "SnoopDogg"


    # Ask user if they want messages to show on screen or keep default and check with command
    # Also ask if they want message confirmations


    # Initialize Client as active with server
    print("Connecting to UDP Chat Server at %s:%d ..." % ( host, port) )
    time.sleep(1)
    print("Requesting username %s ... " % name)
    time.sleep(1)
    pkt = "#./INIT" + msg_break + name
    clientSock.sendto(pkt.encode("ascii"), server)

    # Wait for userId and user list, then parse
    try:   
        msg = clientSock.recvfrom(1026)[0]
        msg = msg.decode('utf-8')
        name, userlist = msg.split(msg_break)
        print("Connected to Chat Server. Your screen name is %s\n" % name)
        print('%s\n' % userlist)
    except Exception as e: 
        print("Error initiating chat client with server." + str(e))
        raise e
    return clientSock, server

def reqUserList():
# Send request to server for most recent active userlist update
    global inbox
    userlist=''
    check, check_inbox_limit= 0, 7
    
    # Generate random control key to append to message to verify update is new  
    update_key = random.randint(1000, 9999)
    req = "#./USER" + msg_break + str(update_key)
    prefix ="#./USER" + str(update_key)
    
    # send request
    try:
        clientSock.sendto(req.encode("ascii"), server)
        print("\nRequesting updated user list ...")
    except Exception as e:
        print("Error requesting user list: %s" % e)

    # Give client listener thread time to add response to ctrl_inbox, then check for response
    while check <= check_inbox_limit:
        time.sleep(resp_wait)
        for msg in ctrl_inbox:
            msg_prefix, userdata = msg.split(msg_break)
            if msg_prefix == prefix:
                return userdata
                break
        if check == check_inbox_limit and userlist == '':
           print("[ERROR] Updated Userlist not found in inbox after waiting %d seconds for %d iterations : %s" % (resp_wait, check_inbox_limit, userlist))
        check +=1  
    return 'Request for userlist has timed out. Userlist unavailable'
def main_loop():
# Start thread to listen for server messages while also waiting for user input
    global stayOnServer
    global inbox
    initial_setup = True

    # Start thread to listen for server responses
    listening_thread = ClientThread(threadID=1, name="Listening Thread", counter=1)
    listening_thread.start()
    
    # Start user interface loop
    while stayOnServer:
        msg = ''    
        if initial_setup:
        # Check if this is first loop iteration, if so get initial destination to initialize destination user before continuing with main loop
            notValid = True
            while notValid: 
                dest = ''
                print("Enter the name of the user you want to message. Enter 'none' or '0' to pick later.")
                try:    
                    dest = raw_input().strip()
                except Exception as e:
                    dest = input()
                notValid = False
                if dest == './user':
                    print('Invalid username, please select a user from the active users list.')
                    notValid = True
                elif dest =='none' or dest =='no one' or dest =='0' or dest == '' or dest == './exit':
                    print("No user selected. Enter ./user to select a user to message.")
                    dest = "no one"
            print("Currently messaging %s" % dest)
            initial_setup= False
        elif not initial_setup:
        # if this is not the first loop iteration, dest is already initiated, so continue interface loop
            print("\nEnter your message for " + dest 
                + ". Enter './user' to change user and './inbox' to view your message inbox. \nEnter ./exit to leave chat server .")
            
            # Included try/catch in all user inputs for conflicting python versions
            try:    
                msg = raw_input().strip()
            except Exception as e:
                msg = input()
        
        if msg == '':
            pass        
        elif msg == './user':
        # If user is requesting user list then send request and get new user destination input 
            
            # Request userlist from server and print it
            userlist = reqUserList()
            print("# %s #\n"%userlist)

            # Get user destination input and set dest
            notValid = True
            while notValid: 
                dest = ''
                print("Enter the name of the user you want to message. Enter none to pick later.")
                try:    
                    dest = raw_input().strip()
                except Exception as e:
                    dest = input()
                notValid = False
                
                if dest == './user' or dest == '':
                    print('Invalid username, please select a user from the active users list.')
                    notValid = True
                elif dest =='none':
                    print("No user selected. Enter ./user to select a user to message.")
                    dest = "no one"
            print("Currently messaging %s" % dest)
        
        elif msg == './inbox': 
        # display all user messages received during this session 
            print("Chat Message Inbox:")
            if len(inbox) == 0: print("No new messages received.")
            else:
                for m in inbox:
                    print("  %s -> \n")
            
        elif msg == './exit': 
        # Send exit message to server and end main loop
            stayOnServer = False
            pkt = "#./EXIT" + msg_break + " #./CONFIRM" 
            print("\nDisconnecting from server ...")
            clientSock.sendto(pkt.encode('ascii'), server)

        else: 
        # If no control messages, then send message to preset destination user
            if dest == name:
                print("Error, you entered your name as the receiving user")
                pass
            elif dest == 'no one':
                print("Error - You have yet to select a user to message. Enter ./user to select a receiving user from the user list.")
            else:
                # Confirm send
                try:    
                    confirm = raw_input("Send message: '%s' to %s? (y/n) " % (msg, dest) ).strip()
                except Exception as e:
                    confirm = input("Send message: '%s' to %s? (y/n) " % (msg, dest) )
                if confirm == 'n' or confirm == 'no' or confirm == 'N':
                    pass
                else:
                # Send user's message with destination user as message prefix
                    pkt = dest + msg_break + msg
                    try:
                        clientSock.sendto(pkt.encode('ascii'), server)
                    except Exception as e: 
                        print("Error sending client msg '%s' to server: %s" % (msg, e) )
                    print("Message sent.")

    
    print("GoodBye!\nPress Enter to Close.")
    try:    
        raw_input().strip()
    except Exception as e:
        input()

# Create thread lock to sync threads
threadLock = threading.Lock()

# initiate client socket and get server data input from user    
clientSock, server = init_client()

# Initiate main messaging interface loop
main_loop()


## IF ALL ELSE FAILS: Just send back and forth and put inbox on server
## Right now im going to put main loop in seperate thread and have main thread rcv 
# Notes: No problem with printing while waiting on input

### New soln: use locks to keep threads synced and thread.join() to only close once they are all finished
## - Check if I can just run synced sending and recieving threads on same port 
### User input soln: input takes in you input as an evaluated expression, raw_input gets just the string
#### IDEA: Lock all thread functions not using socket or just test whether locked threads can use same socket
#### RECALL: You're running py3 in terminal, but py2 by default. each will throw an error on other's input. 
# Keep in mind when making exe - quick fix with try/catch

# TODO: 
# Include user input for ports, server, name
# send server exit message to close the connection and remove user from active users list
   # -- Since client is always listening, can server just send out userlist when new user joins?
# see if printing incoming msgs while waiting on input is possible with
# After that: 
  # Allow users to select multiple destinations