﻿# UDP Chatroom Application

## Purpose

Chat Application which uses the UDP network protocol to allow connected clients to send messages to one or more recipients connected to the chat server.

## Instructions

### Launching the Server:
I. Run the 'Server-UDP' executable and Enter the port on which you want the Server to run. It is port 9997 by default


### Lauching the Client:
*Press Enter to use default values
I. Run the 'Client-UDP' executable and Enter the port on which you want the Client to run. It is port 9998 by default

II. Enter the port of the Chat Server you wish to connect to. It is port 9997 by default.

III. Enter your preferred screen name. It is 'Client' by default

IV. You will be prompted about streaming messages to the screen as they are recieved. This is disabled by default. 

V. The client will send your username to the server to be initiated and recieve a list of currently active users on the chat server. 
You will then be asked to pick a user or group of users to message. After which you will be taken to the main user interface loop. 

VI. At anytime while recieving and sending messages you may press enter to show the control commands which You are available to you. 
You will have the options to update user list and destination user, display the messages recieved in your inbox, or disconnect from the server using the control commands

VII. Any text that is not a control command while be accepted as a message to the currently set destination user. 
You can change your destination user in the messaging prompt by entering ./user instead of a message. 
Exit the server while in the message prompt by entering ./exit
