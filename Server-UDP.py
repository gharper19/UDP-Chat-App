import threading
import socket
import random

exitFlag = 0
class ServerThread (threading.Thread):
    def __init__(self, threadID, name, counter, clientAddr, clientData, newUser=False):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.clientAddr = clientAddr
        self.clientData = clientData
        self.newUser = newUser
    def run(self):
        # Call methods here
        if self.newUser: 
            init_user(self.clientAddr, self.clientData, self.name) 
        else: 
            handle_user(self.clientAddr, self.clientData, self.name)

'''
# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()

'''


################## Server Code ####################



# Debugging 
thread_limit = 5

# User list - Dictionary { userID : IP address }, IP is reverse to retrieve usernames
users = {}
IPs = {}

# Message log
msg_log = {}

def init_server():
    # Initialize Server Socket as UDP 
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind Server Socket to host
    serverHost = '127.0.0.1' # socket.gethostbyname(socket.gethostname()) #
    serverPort = 9997
    serverSock.bind((serverHost, serverPort))

    print("Server Initialized at %s" % serverSock)
    return serverSock 
        
def init_user(clientAddr, clientData, threadName):
# Add client to lists and send back username and IP address
    clientData = clientData.decode('utf-8')
    print(threadName + ": Connection Recieved from " + clientAddr[0] + str(clientAddr[1]) + " requesting username " + clientData)
    
    # Add client to user list using given user name + 4 random digits
    reroll = True
    while reroll:
        username = clientData + str(random.randint(1000, 9999))
        if not username in users.keys():
            # If name not taken record name and IP 
            users[username] = clientAddr
            IPs[clientAddr] = username
            reroll= False
        else:
            print("Username %s unavailable" % username)  

    # Send list of connected users to newly initialized user 
    if len(users.keys()) == 0:
                    userlist = ''
    else:
        for name in users:
            try:
                if name == users.keys()[len(users)-1]:
                    userlist += name
                else: userlist += name + ' - '
            except Exception as e: 
                print("-- Userlist Empty -- KeyError with list concatentation")
                userlist = '[Empty]'
    resp = username + " /$MESSAGE_BREAK: " + userlist
    serverSock.sendto(
        resp.encode('ascii'), 
        clientAddr 
        ) 
    print("New User %s Initialized!" % username)

def handle_user(clientAddr, clientData, threadName):
    print(threadName + ": Message Recieved from " + str(IPs[clientAddr]) + " at " + str(clientAddr)  + " requesting username " + clientData.decode('utf-8') )
    
    # Client UDP Data must be delimited to determine message receiver 
    rcv_user, user_msg = clientData.decode('utf-8').split(" /$MESSAGE_BREAK: ")[0], clientData.split(" /$MESSAGE_BREAK: ")[1]
    try: 
        # ! Add error handling for user not found and user is self
        message = "From " + IPs[clientAddr] + ': ' + user_msg      
        rcv_addr, rcv_port =  users[rcv_user]         
        print("User %s messaging %s at %s:%d .." % str(users[clientAddr]), rcv_user , rcv_addr, rcv_port)
        serverSock.sendto(message.encode, (rcv_addr, rcv_port))
    except Exception as e: 
        print("Error Handling User Messaging: " + str(e))

    # Send message to receiving IP address and port
    print("Message Sent!"); 

# ! strip() strings on user input
def main_loop():
    print("Server Online ... Waiting for connections: \n")
    threadCount = 1
    # Keep Server Process running prepared for clients - start a new thread for each client
    
    while True:    
        clientData, clientAddr = serverSock.recvfrom(1024)
        print(clientAddr, clientData)
        # client_ip = "%s:%d" clientAddr.split
        # Check on num threads and thread limit

        # Check for empty messages
        if clientData.decode('utf-8') == "":
            pass
        
        # Check for control messages - # new thread
        elif clientData.decode('utf-8') == '#./USER':
            if len(users.keys()) == 0:
                    userlist = ''
            else:
                for name in users:
                    try:
                        if name == users.keys()[len(users)-1]:
                            userlist += name
                        else: userlist += name + ' - '
                    except Exception as e: 
                        print("-- Userlist Empty -- KeyError with list concatentation")
                        userlist = '[Empty]'
            resp = '#./USER /$MESSAGE_BREAK: %s' % userlist
            serverSock.sendto(resp.encode, (clientAddr, clientData))
        
        # If new user, recieve username and add to user listen else send user's message
        elif clientAddr in users.values():
            # Handle message for known user
            s = ServerThread(threadCount, "Thread-%d" % threadCount, threadCount, 
                clientAddr, clientData, newUser=False)
            threadCount+=1
            s.start()
        else: 
            s = ServerThread(threadCount, "Thread-%d" % threadCount, threadCount, 
                clientAddr, clientData, newUser=True)
            threadCount+=1
            s.start()

serverSock = init_server()
main_loop()

# socket.setdefaulttimeout(timeout) 
# recv(bufsize) vs recvfrom() 


# def if __name__ == "__main__":
#     pass