import time
import socket
import sys
import random
import threading
import socket

exitFlag = 0
class ClientThread (threading.Thread):
# Listens on global clientSocket for messages from server
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    
    def run(self):
        global stayOnServer
        global inbox
        global ctrl_inbox
        global streamInbox

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
                    # print("[INFO] [DEBUG] CTRL Inbox: " + str(ctrl_inbox))
                elif "#./EXIT" in prefix:
                    stayOnServer = False
                elif "#./ERROR_INVALID_USER" in prefix:
                    ctrl_inbox += [clientData]
                    print("Recent message '%s' failed to send. Destination user was not found in active userlist."
                        % data)
                else: 
                    inbox += [data]
                    time.sleep(2)
                    # print("[INFO] [DEBUG] Inbox: " + str(inbox))
                    if streamInbox:
                        print("> " + str(data)+ '\n')        
                
                threadLock.release()
            except Exception as e:
                print("Error receiving messages from server %s: %s" % (str(server) , e))


msg_break = " /$MESSAGE_BREAK: "
stayOnServer = True
streamInbox= False
resp_wait= 1

name = ''
inbox=[]
ctrl_inbox = []
user_groups = {}


def init_client():
# Get user data for establishing connection and request username and userlist from server 
    global streamInbox

    # Init and bind client socket
    clientHost = '127.0.0.1'
    clientPort = 9998
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print("Enter the port that the messager client should use. Enter nothing to use default port %d" % clientPort)
    try:    
        t = raw_input().strip()
    except Exception as e:
        t = input()
    if not t == '':
        clientPort= int(t)
    
    try:
        clientSock.bind((clientHost, clientPort)) 
    except Exception as e: 
        clientPort = 9998
        clientSock.bind((clientHost, clientPort)) 
        print("Error with chosen port. Using default port %d" % clientPort)

    # Get Server IP and port
    host = '127.0.0.1' 
    port = 9997
    server = (host,port)
    print("Enter the port for the chat server.")
    try:    
        t = raw_input().strip()
    except Exception as e:
        t = input()
    if not t == '':
        port= int(t)

    # Get username
    name = 'Client'
    print("Enter your username for the chat server.")
    try:    
        t = raw_input().strip()
    except Exception as e:
        t = input()
    if not t == '':
        name= t


    # Ask user if they want messages to show on screen or keep default and check with command
    resp = ''
    print("\nMessages are accessed by the ./inbox control command in the interface by default.\n"
        + "Would you like for messages to be shown as they are received instead? (y/n)")
    try:    
        resp = raw_input().strip()
    except Exception as e:
        resp = input()
    
    if resp == 'n' or resp == 'no' or resp == 'N' or resp == '':
        streamInbox = False
    else:
        streamInbox = True
    
    # Initialize Client as active with server
    print("\nConnecting to UDP Chat Server at %s:%d ..." % ( host, port) )
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
    global name

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
                # Allow user to enter a single name, or multiple names delimited by commas to create a group message and ask for an identifier for group
                print("Enter the name of the user or group you want to message."
                    + "To create a group message, enter the names of the users you would like to message with each seperated by commas.")
                print("Enter 'none' or '0' to pick your destination user later.")
                try:    
                    dest = raw_input().strip()
                except Exception as e:
                    dest = input().strip()
                
                # Assume user input is valid and proceed with checks
                notValid = False
                if dest == './user':
                # Check if accidentally entered control message
                    print('Invalid username, please select a user from the active users list.')
                    notValid = True
                elif ',' in dest:
                # Check if group message
                    users = dest.split(',')
                    userstring = ''
                    for name in users:
                        if name == ' ' or name == '':
                            del name
                        else:
                            userstring += name.strip()
                            if not name == users[len(users)-1]:
                                userstring += ', '
                    # print("Enter a name for your new message group of users: %s" % userstring)
                    # try:    
                    #     groupName = raw_input().strip()
                    # except Exception as e:
                    #     groupName = input().strip
                    
                    # Set group name and add to destination
                    # user_groups[groupName] = userstring
                    dest = userstring
                
                elif dest =='none' or dest =='no one' or dest =='0' or dest == '' or dest == './exit':
                    print("\nNo user selected. Enter ./user to select a user to message.")
                    dest = "no one"
            print("Currently messaging %s" % dest)
            initial_setup= False
        elif not initial_setup:
        # if this is not the first loop iteration, dest is already initiated, so continue interface loop
            print("\nEnter your message for " + dest 
                + ". Enter './user' to change destination user and './inbox' to view your message inbox."
                + "\nEnter ./exit to leave chat server.")
            
            # Included try/catch in all user inputs for conflicting python versions
            try:    
                msg = raw_input().strip()
            except Exception as e:
                msg = input()
        
        if msg == '':
        # Bring up command menu again if message is empty
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
                print("Enter the name of the user or group you want to message."
                    + "To create a group message, enter the names of the users you would like to message with each seperated by commas.")
                print("Enter 'none' or '0' to pick your destination user later.")

                try:    
                    dest = raw_input().strip()
                except Exception as e:
                    dest = input()
                notValid = False
                
                if dest == './user' or dest == '':
                    print('Invalid username, please select a user from the active users list.')
                    notValid = True
                elif ',' in dest:
                    # Check if group message
                    users = dest.split(',')
                    userstring = ''
                    for name in users:
                        if name == ' ' or name == '':
                            del name
                        else:
                            userstring += name.strip()
                            if not name == users[len(users)-1]:
                                userstring += ', '
                    # print("Enter a name for your new message group of users: %s" % userstring)
                    # try:    
                    #     groupName = raw_input().strip()
                    # except Exception as e:
                    #     groupName = input().strip
                    
                    # Set group name and add to destination
                    # user_groups[groupName] = userstring
                    dest = userstring
                elif dest =='none':
                    print("No user selected. Enter ./user to select a user to message.")
                    dest = "no one"
            print("Currently messaging %s" % dest)
        
        elif msg == './inbox': 
        # display all user messages received during this session 
            print("\nChat Message Inbox:")
            if len(inbox) == 0: print("No new messages received.")
            else:
                for m in inbox:
                    print("> %s\n" % m)
            
        elif msg == './exit': 
        # Send exit message to server and end main loop
            stayOnServer = False
            pkt = "#./EXIT" + msg_break + " #./CONFIRM" 
            print("\nDisconnecting from server ...\n")
            clientSock.sendto(pkt.encode('ascii'), server)

        else: 
        # If no control messages, then send message for preset destination user to the server
            send = dest
            if send in user_groups.keys():
                send = user_groups[send]
            if send == name:
                print("Error, you entered your name as the receiving user")
                pass
            elif send == 'no one':
                print("Error - You have yet to select a user to message. Enter ./user to select a receiving user from the user list.")
            else:
                # Confirm send
                try:    
                    confirm = raw_input("Send message: '%s' to %s? (y/n) " % (msg, send) ).strip()
                except Exception as e:
                    confirm = input("Send message: '%s' to %s? (y/n) " % (msg, send) )
                if confirm == 'n' or confirm == 'no' or confirm == 'N':
                    pass
                else:
                # Send user's message with destination user as message prefix
                    pkt = send + msg_break + msg
                    try:
                        clientSock.sendto(pkt.encode('ascii'), server)
                    except Exception as e: 
                        print("Error sending client msg '%s' to server: %s" % (msg, e) )
                    print("Message sent.")
    print("GoodBye! Press Enter to Close.")

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
