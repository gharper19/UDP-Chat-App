import threading
import socket
import random

exitFlag = 0
class ServerThread (threading.Thread):
    def __init__(self, threadID, name, counter, clientAddr, clientData, newUser=False, sendUsers=False):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.clientAddr = clientAddr
        self.clientData = clientData
        self.newUser = newUser
        self.sendUsers = sendUsers
    def run(self):
        # Call methods here
        if self.newUser: 
            init_user(self.clientAddr, self.clientData, self.name) 
        elif self.sendUsers:
            sendUserList(self.clientAddr, self.clientData)
        else: 
            handle_user(self.clientAddr, self.clientData, self.name)


################## Server Code ####################


# Debugging 
thread_limit = 99

# User list - Dictionary { userID : IP address }, IP is reverse to retrieve usernames
users = {}
IPs = {}
msg_break =' /$MESSAGE_BREAK: '
remoteKillServerCmd = "#./KILLSERVER"

# Initialize Server Socket as UDP 
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind Server Socket to host
serverHost = '127.0.0.1' # socket.gethostbyname(socket.gethostname()) #
serverPort = 9997
serverSock.bind((serverHost, serverPort))
bufferSize = 1024

        
def init_user(clientAddr, clientData, threadName):
# Add client to lists and send back username and IP address

    reroll = True
    while reroll:
        # Add client to user list using given user name + 4 random digits
        username = clientData + str(random.randint(1000, 9999))
        if not username in users.keys():
            # If name not taken record name and IP, continue
            users[username] = clientAddr
            IPs[clientAddr] = username
            reroll= False
        else:
            print("Username %s unavailable" % username)  

    # Send server screen name with appended list of connected users to newly initialized user 
    resp = username + msg_break + compileUserList(username)
    serverSock.sendto(resp.encode("ascii"), clientAddr)
    print("[INFO] [INIT_USER] %s: New client %s:%d assigned username: %s" % (threadName, clientAddr[0], clientAddr[1], username) ) 

def handle_user(clientAddr, clientData, threadName):
# Check that user destination is valid, then send message to destination 
    print("[INFO] [SND_MSG] %s: Message Received from %s:%d - %s" % (threadName, clientAddr[0], clientAddr[1], clientData.decode('utf-8') ))
    
    # Separate Client UDP Data into rcv user and actual message data 
    rcv_user, user_msg = clientData.decode('utf-8').split(msg_break)[0],clientData.decode('utf-8').split(msg_break)[1]
    
    # check if rcv_user is valid, if not respond with error code and exit function
    if rcv_user == IPs[clientAddr] or rcv_user not in users.keys():
        resp = "#./ERROR_INVALID_USER" + msg_break + clientData
        serverSock.sendto(resp.encode('ascii'), clientAddr)
        print("[ERROR] [SND_MSG] Destination user is invalid. Cannot send message '%s':%s" 
            % (clientData.decode('utf-8'), str(e) ) )
        return
   
    # Send users message to intended user
    try: 
        message = "From " + IPs[clientAddr] + ': ' + user_msg      
        rcv_addr, rcv_port =  users[rcv_user]         
        serverSock.sendto(message.encode('ascii'), (rcv_addr, rcv_port))
        print("[INFO] [SND_MSG] User %s has sent message '%s' to  %s at %s:%d .." 
            % (IPs[clientAddr], user_msg, rcv_user , rcv_addr, rcv_port)) 
    except Exception as e: 
        print("[ERROR] [SND_MSG] Error sending user message '%s':%s" 
            % (clientData.decode('utf-8'), str(e) ) )

def compileUserList(clientName):
    # Compile User list
    userlist = 'Active Users: '
    usernames = list(users.keys())
    if len(usernames) == 0:
        userlist = 'You are the first to connect to the server!'
    else:
        for name in usernames:
            try:
                if name == usernames[len(users)-1]:
                    if name == clientName:
                        userlist += name + "(you)"
                    else:
                        userlist += name
                else: 
                    if name == clientName:
                        userlist += name + "(you)" + ' - '
                    else:
                        userlist += name + ' - '
            except Exception as e: 
                print("[ERROR] [compileUserList] -- Userlist Empty -- KeyError with list concatentation: " + e)
                userlist = '[Empty]'
    return userlist

def sendUserList(clientAddr, clientData):
# Compile all usernames into a string, mark user with '(you)', and send to requesting user 
    clientData = clientData.decode("utf-8")
    clientName = IPs[clientAddr]
    userlist = compileUserList(clientName)
    
    # Compile Ctrl prefix from Ctrl msg and update code
    msg_prefix = clientData.split(msg_break)[0] + clientData.split(msg_break)[1]
    
    # return userlist with user control id confirmation
    try:
        resp = msg_prefix + msg_break + userlist
        serverSock.sendto(resp.encode('ascii'), clientAddr)            
    except Exception as e:
        print("[ERROR] [SEND_USERLIST] Error Sending user list: %s" % e)

def main_loop():
# Begin serving clients
    print("Server Online at %s:%s... Waiting for connections: \n" % (serverHost, serverPort) )
    threadCount = 1
    
    # Keep Server Process running prepared for clients - start a new thread for each client
    while True:   # use thread limit here
        msg_prefix, clientMsg = '', ''
        try:
            clientData, clientAddr = serverSock.recvfrom(bufferSize)
        except Exception as e:
            print("[ERROR MAIN] Error receiving client datagram with buffer size %d: %s" % (bufferSize, str(e)))
        

        # Debugging message
        print("[INFO MAIN] Recieved datagram: %s - From: %s:%d" % (clientData, clientAddr[0], clientAddr[1]))


        if msg_break in clientData.decode('utf-8'):
            msg_prefix, clientMsg = clientData.decode('utf-8').split(msg_break)
        else:
            print("Formmatting error with client message: %s" % clientData.decode('utf-8'))
            msg_prefix = ''
            clientMsg = ''

        # Check for empty messages or control messages
        if clientMsg == "":
            pass
        
        elif clientMsg == remoteKillServerCmd:
        # Admin control command to terminate server 
            break
        
        elif msg_prefix == "#./INIT": 
        # If new user, start new thread to receive username, add client to user list
            s = ServerThread(threadCount, "Thread-%d" % threadCount, threadCount, 
                clientAddr, clientMsg, newUser=True)
            threadCount+=1
            s.start()
        
        elif msg_prefix == '#./USER':
        # Send user current userlist with requesting user marked with '(you)'
            s = ServerThread(threadCount, "Thread-%d" % threadCount, threadCount, 
                clientAddr, clientData, newUser=False, sendUsers=True)
            threadCount+=1
            s.start()
        
        elif msg_prefix == '#./EXIT':
        # Remove user from userlist and respond with confirmation of disconnection
            try:
                print("[INFO] User %s at %s:%d is disconnecting" % (IPs[clientAddr], clientAddr[0], clientAddr[1]))
                del users[IPs[clientAddr]]
                del IPs[clientAddr]
                
                # Acknowledge disconnect with client
                pkt ="#./EXIT" + msg_break + '#./CONFIRMED'
                serverSock.sendto(pkt.encode('ascii'), clientAddr)
                
                print("[INFO] Client %s:%d successfully disconnected." % (clientAddr[0], clientAddr[1]))
            except Exception as e:
                print("Error: Exiting user not found in userlist: %s" % e)
        
        elif clientAddr in users.values():
        # if user is in active user list start thread to send user's message to destination
            # handle user not found and multiple users
            s = ServerThread(threadCount, "Thread-%d" % threadCount, threadCount, 
                clientAddr, clientData, newUser=False)
            threadCount+=1
            s.start()

try:
    main_loop()
except Exception as e: 
    input("Server FAILURE: %s\nPress Enter to Exit" % e)