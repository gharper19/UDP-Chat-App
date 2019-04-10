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
        # print("Starting %s" % self.name)
        
        global stayOnServer
        global inbox
        global ctrl_inbox

        # Listening loop waiting for messages from the Server  
        while stayOnServer:
            try:
                clientData = clientSock.recvfrom(1026)[0].decode('utf-8')
                
                # Acquire thread lock to assure this runs with main thread
                threadLock.acquire()

                # Check for message break
                if msg_break in clientData:
                    prefix, data = clientData.split(msg_break)
                else:
                    prefix
                    data = clientData
                
                if "#./USER" in prefix:
                    ctrl_inbox += [clientData]
                    print("[INFO] CTRL Inbox: " + str(ctrl_inbox))
                elif "#./EXIT" in prefix:
                    stayOnServer = False
                else: 
                    inbox += [data]
                    print("[INFO] MSG Inbox: " + str(inbox))        # Issue printing while taking input?
                
                # Acquire thread lock to assure this runs with main thread
                threadLock.release()
            
            except Exception as e:
                print("Error receiving messages from server %s: %s" % (str(server) , e))

################## Client Code ####################


msg_break = " /$MESSAGE_BREAK: "
stayOnServer = True
resp_wait= 1

name = ''
inbox=[]
ctrl_inbox = []

## Get user input
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
    name = "SnoopDogg"

    # Initialize Client as active with server
    print("Connecting to UDP Chat Server at %s:%d ..." % ( host, port) )
    time.sleep(1)
    print("Requesting username %s ... \n" % name)
    pkt = "#./INIT" + msg_break + name
    clientSock.sendto(pkt.encode("ascii"), server)

    # Wait for userId and user list, then parse
    msg = clientSock.recvfrom(1026)[0]
    msg = msg.decode('utf-8')
   
    try:   
        name, userlist = msg.split(msg_break)
        print("Connected to Chat Server. Your screen name is %s" % name)
        print(userlist)
    except Exception as e: 
        print("Error Initiating with server." + str(e))
        raise e
    return clientSock, server

def reqUserList():
    global inbox
    
    # Request User List with appended random number to determine most recent
    userlist=''
    check, check_inbox_limit= 0, 7
    
    update_key = random.randint(1000, 9999)
    req = "#./USER" + msg_break + str(update_key)
    prefix ="#./USER" + str(update_key)
    try:
        clientSock.sendto(req.encode("ascii"), server)
        print("Requesting updated user list ...\n")
    except Exception as e:
        print("Error requesting user list: %s" % e)

    # Give receiver thread time to add to control inbox and check for response
    while check <= check_inbox_limit:
        time.sleep(resp_wait)
        for msg in ctrl_inbox:
            msg_prefix, userdata = msg.split(msg_break)
            if msg_prefix == prefix:
                return userdata
        if check == check_inbox_limit and userlist == '':
            return "Updated Userlist not found in inbox after waiting %d seconds for %d iterations" % (resp_wait, check_inbox_limit)
        # if check < 2:
        #     input("Continue? Press Enter")
        check +=1  
        print("Inbox check %d: %s" % (check, ctrl_inbox))

def main_loop():
# Start thread to listen for server messages while also waiting for user input
    listening_thread = ClientThread(threadID=1, name="Listening Thread", counter=1)
    listening_thread.start()

    global stayOnServer
    global inbox

    setDest = True
    debug_flag=1
    while stayOnServer: 
        # Check if this is first loop iteration
        if setDest:
        ## Include list of delimited clients as raw_input option for group messages 
            
            notValid = True
            # print("# %s #\n"%userlist)
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
            setDest= False




        if not setDest:
            print("\nEnter your message for " + dest 
                + ". Enter ./user to change user and ./exit to leave chat server. Enter ./inbox to view your message inbox.")
            try:    
                msg = raw_input().strip()
            except Exception as e:
                msg = input()
        
        # if debug_flag == 1:
        #     msg = './user'
        #     debug_flag += 1
        # elif debug_flag == 2:
        #     time.sleep(1)
        #     msg = './inbox'
        # elif debug_flag > 5: 
        #     # End early
        #     return

        # Check for control commands
        if msg == './user':
        # If user is requesting user list then send request and get destination input 
            userlist = reqUserList()
            print("# %s #\n"%userlist)

            ## Include list of delimited clients as raw_input option for group messages 
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
            print("Chat Message Inbox:\n")
            if len(inbox) == 0: print("No new messages received.")
            
        elif msg == './exit': 
            stayOnServer = False
            pkt = "#./EXIT" + msg_break + " #./CONFIRM" 
            print("\nDisconnecting from server ...")
            clientSock.sendto(pkt.encode('ascii'), server)

        else: 
        # If no control messages, then send message to preset destination user
            if dest == name:
                print("Error, you entered your name as the recieving user")
                pass
            elif dest == 'no one':
                print("Error - You have yet to select a user to message. Enter ./user to select a receiving user from the user list.")
            else:
                # Confirm send
                print("Send message: '%s' to %s? (y/n)" % (msg, dest) )
                try:    
                    confirm = raw_input().strip()
                except Exception as e:
                    confirm = input()
                if confirm == 'n' or confirm == 'no':
                    pass
                else:
                # Send user's message with destination user as message prefix
                    pkt = dest + msg_break + msg
                    try:
                        clientSock.sendto(pkt.encode('ascii'), server)
                    except Exception as e: 
                        print("Error sending client msg '%s' to server: %s" % (msg, e) )
                    print("Message sent!")

    print("GoodBye!\nPress Enter to Close.")
    try:    
        raw_input().strip()
    except Exception as e:
        input()
# Create thread lock to sync threads
threadLock = threading.Lock()

# Gets users name, initiates socket , and gets username and userlist from server    
clientSock, server = init_client()
main_loop()

# rcvs name and list, user ctrl gives error

# IF ALL ELSE FAILS: Just send back and forth and put inbox on server
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