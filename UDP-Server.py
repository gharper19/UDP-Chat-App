import threading
import socket

# Initialize Server Socket 
serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind Server Socket to host
serverHost = '127.0.0.1' # socket.gethostbyname(socket.gethostname()) #
serverPort = 9998
serverSock.bind((serverHost, serverPort))

# User list - Dictionary {userName: IP-Address}
users = {}


# IP list - {IP: username}
IPs = {}

# Message log
msg_log = {}

# Keep Server Process running prepared to print client requests
print(f"Server Online at {serverHost}... Waiting for connections: \n")
while True:    
    clientData, clientAddr = serverSock.recv(4092)
    print("Connection Recieved from " + clientAddr + " messaging username " + clientAddr )
    # Try to check for Client IP in user list
    try: 
        if clientAddr in users:
            # Client UDP Data must be delimited to determine message receiver 
            try: 
                message = "From " + IPs[clientAddr] + ': ' + clientData.split(" /$MESSAGE_BREAK: ")[1]
                
                # Get IP address from user list
                destination = users[clientData.split(" /$MESSAGE_BREAK: ")[0]].trim()
                
                # Separate Address and port by ':' delimiter
                rcv_addr, rcv_port = destination.split(':')[0], destination.split(':')[1]
                
                print("User " + users[clientAddr] + " sending message to "+  users[destination] +  " at  " + destination + " ...")

                # EExit for now 
                input("Done Processing.. Press Enter"); break
            except Exception as e: 
                print("Formatting Error: " + str(e))
                break
            
            # Send message to receiving IP address and port
            serverSock.sendto(message.encode, (rcv_addr, rcv_port))

        # Just in case check for user does not throw an exception to initialize unknown user  
        else: raise Exception

    # Initialize user if not in user list 
    except Exception as e:
        print("Connection Recieved from " + clientAddr + " requesting username " + clientData )
        # Add client to user list using given user name 
        users[clientData] = clientAddr

        # Add Username to IP list
        IPs[clientAddr] = clientData

        # Send list of connected users to newly initialized user 
        serverSock.sendto(
            str(users).encode, 
            (clientAddr.split(':')[0], clientAddr.split(':')[1]) 
            ) 
        input("Done Processing.. Press Enter"); break

input("Enter to close")
#socket.setdefaulttimeout(timeout) 
# recv(bufsize) vs recvfrom() 