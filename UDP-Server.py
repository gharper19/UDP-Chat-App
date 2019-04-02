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

    print("Server Initialized at %s", str(serverSock))
    return serverSock 

'''
def recieve_message(clientAddr, clientData): 
    # Client UDP Data must be delimited to determine message receiver 
    rcv_user = clientData.split(" /$MESSAGE_BREAK: ")[0]
    try: 
        message = "From " + IPs[clientAddr] + ': ' + clientData.split(" /$MESSAGE_BREAK: ")[1]
        
        # Add error handling for user not found


        # Get IP address from user list
        destination = users[rcv_user]
        
        # Separate Address and port by ':' delimiter
        rcv_addr, rcv_port = destination.split(':')[0], destination.split(':')[1]
        
        print("User " + users[clientAddr] + " sending message to "+  users[destination] +  " at  " + destination + " ...")

        # EExit for now 
        input("Done Processing.. Press Enter"); 
    except Exception as e: 
        print("Formatting Error: " + str(e))
        break

    # Send message to receiving IP address and port
    serverSock.sendto(message.encode, (rcv_addr, rcv_port))
'''
        
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
    resp = username + " /$MESSAGE_BREAK: " + str(users.keys) 
    serverSock.sendto(
        resp.encode('ascii'), 
        clientAddr 
        ) 
    print("New User Initialized!")

def handle_user(clientAddr, clientData, threadName):
    print(threadName + ": Message Recieved from " + IP[clientAddr] + " at " + clientAddr  + " requesting username " + clientData )
    
# ! Each User gets a thread on the server
def main_loop():
    print("Server Online ... Waiting for connections: \n")
    threadCount = 1
    # Keep Server Process running prepared for clients - start a new thread for each client
    
    while True:    
        clientData, clientAddr = serverSock.recvfrom(1024)
        # client_ip = "%s:%d" clientAddr.split
        # Check on num threads and thread limit

        # If new user, recieve username and add to user listen
        if clientAddr in users.values():
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