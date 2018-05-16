# multiclient_chat_server_application

## Introduction

The  basic  purpose  of  a  chatroom  is  to  provide  users  a  way  of  sharing  information  with  a  group  of  otherusers realtime.  Users can share information using wide variety of media ranging from texts or images or evenlive streaming.  Chatrooms are generally used between users having a shared internet connection and allowsfor instantaneous messaging between the whole group or a private messaging between two or more users.Apart from having the basic functionality of sending messages chatrooms provide many other features forusers so that they can tailor their chatroom experience in any way they want to.  For example users can nowblock(unblock) other users in the chatroom, so they can control what messages they see and what messagesthey don’t.

## Objectives
Our objective was to build a chatroom with the following features:
### •Chatroom supports broadcast and p2p messaging.
### •Has the basic security features of a chat room(Authentication).
   –Clients log in to the server using their username and password.
    –Blocks user for 60 seconds after three unsuccessful login attempts.This is done to prevent peoplefrom brute forcing a password.
    –Only one session per user is allowed i.e.  duplicate login’s are not allowed.
### •Users are provided with useful commands using which they can look at other logged in users.
    –whoelse:Displays all the currently logged users.
    –wholasthr:Displays all the logged in users within the last one hour.•Users can block/unblock other users.
### •Users can send messages to offline users(Asynchronous messaging).•Users can logout using the logout command

## Architecture
There  are  two  python  files  server.py  and  client.py.The  server  is  setup  by  running  the  server.py  file  andproviding the port as an argument.The main implementation of the chat application consists of the followingcomponents:

### •Socket Programming:Sockets are end points of communication.These are used to establish communication between processeson the same machine or different machines.For our application we are going to set up a socket on theserver side and keep it running.Each client sets up their own socket and connects to the server socketusing  the  IP  and  PORT  of  the  server  socket.The  client  can  then  interact  with  other  clients  via  theserver.
### •Multi-Threading:The purpose of multi threading is to allow all users to independently interact with the server simulta-neously.  Whenever a user tries to connect to the server socket we are going to make a new thread forthat user in which he can interact with the server.If we haven’t done this, then the server can listen toonly one connection at a time.  Simultaneous requests from different processes can’t be done withoutmulti-threading .We have declared a thread as main thread which aborts all the child threads when itis aborted.
### •Signal Handling:This purpose of using this feature to properly close the connection and update all the datasets whenthe user abruptly.For example ::  When the terminal is closed when it is still running, when the userenters Ctrl+C and aborts the process.  In these cases, the connection is cut properly and the list ofonline users are updated accordingly

## Implementation in brief
The Server Script:
### •Parse client credentials data and blocked users data from the clients.txt file.
### •Create a socket and attach it to the HOST IP address and provided PORT number.
### •Make this socket a server socket.•Make this thread a deamon thread so that all the children threads quit when the main program ends.
### •Listen for any incoming connections.
### •Upon receiving a new connection from a user make a new thread for handling that user.
The following steps occur in the created thread.
–Receive username from the client.
–Check if the user exits.
–If the user doesn’t exist or he is already logged in,show error and ask for user name again.
–if user exists and he is not logged in though any other process,then ask for password.
–If password is correct then go to the next step,if password is wrong,ask for password again if thenumber of tries is less than 3,else lock the account for 60 seconds.
–Add the user to online users.
–Listen for any commands from the client.
–If command is not valid print error message and go to the previous step.
If command is valid andis log-out or CTRL-C(keyboard interrupt) then go to the next step.If command is valid and is notlog-out or CTRL-C then execute the command and go to the previous step.
–Remove the client from online users.–Exit the thread.2
 ### Keep on listening for any new connections in the main thread.
 The Client Script:
 ### •Create the client socket and bind them to client’s IP and a random port number between 1100 and65000.
 ### •Try to connect to the server, if connected move to the next step else raise exception.
 ### •Receive message request for username and password from the user and send credentials to the server.Ifsuccessfully authenticated move to the next step.
 ### •Create a listener thread and make it the deamon thread.The listener thread receives and prints anymessage it receives from any of the clients via the server.
 ### •Send any of the commands the user types to the server.Repeat this step until the user types pressesCTRL-C.
 The features and corresponding commands we have implemented are as follows:
 ### •Block/Unblock:”block/unblock clientname ”Prevents any of the messages from the provided clientname from reaching the user.
  ### •Online Users:”whoelse/wholasthtr”whoelse :  Displays the currently logged in users.wholasthr:  Displays all users who logged in the last one hour.
  ### •P2P message:”message clientname messagecontent ”Send  the  message  to  the  user  with  the  clientname  provided.In  case  the  user  is  offline,  it  keeps  themessage in the mailbox and sends it when the client is back online.
  ### •Broadcast:”broadcast messagecontent ”Broadcast a message to all logged in users.
  ### •offline:”offline”Prints the offline messages of the particular client.
  ### •Logout:”logout”Closes the connection with the server.Additional Features Implemented ::
  ### •Ping:”ping clientname ”Checks  the  status  of  other  client,  i.e  ,whether  it  is  online  or  not,  has  the  other  client  blocked  therequesting user or not
  ### •Creating custom groups:”create group groupname><member1><member2>....”Create a new group with the specified members.
  ### •Messaging to a group”message group groupname messagecontent ”Message the group with the specified group name the contents of the message.
  ### •List of a user’s groups”grouplist”Lists all the groups in which the current client is present
  
  ## Implementation Environment
  ### •Language Used:Python
  ### •Packages Used:socket,multiprocessing,signal,os,time,threading,datetime
