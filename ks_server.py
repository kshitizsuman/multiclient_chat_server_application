import sys,os
import socket,signal,os,time
from multiprocessing import Lock
import threading,datetime

clients_credentials = []
clients_object = []
online_users = []
locked_out_users = []
last_active = {}
PORT_NUM =""
HOST = ""
blocked_list = {}
lock = Lock()
RECV_SIZE = 1024
groups = {}

class client:
	num_of_clients = 0
	def __init__(self, username, password):
		self.username = username
		self.password = password
		self.port = 0
		self.ip = ''
		self.mailbox = []

	def __str__(self):
		return self.username



def logout_user(username):
	global last_active
	global online_users
	online_users = [item for item in online_users if item != username]
	last_active[username] = datetime.datetime.now()

def unlockuser(username):
	global locked_out_users
	time.sleep(60)
	locked_out_users = [item for item in locked_out_users if item != username]
	print username + " 's account has been unlocked !!"
	return 0

def daemon():
	global lock
	global clients_object
	'''lock.acquire()
	try:
		for client in clients_object:
			if client.logged_in == True and client.active == False:
				client.logged_in = False
				#broadcast_message(client.username + ' logged out', client.username,False)
			client.active = False
	finally:
		lock.release()'''
	
	for user in online_users:
		last_active[user] = datetime.datetime.now()
	time.sleep(60)
	main_thread = threading.Thread(name = 'daemon',target = daemon)                       #making it as daemon thread
	main_thread.setDaemon(True)                                                    
	main_thread.start() 

	return(0)


def group_message(message,group_name,sender):
	global groups
	members = groups[group_name]
	message = " @" + group_name + " " + message
	for member in members:
		if (member != sender) and (sender not in blocked_list[member]):
			private_message(message,sender,member)
		else:
			pass
	print sender + " @" +group_name +" :: " + message

def broadcast_message(message,sender):
	global clients_object
	global blocked_list
	global online_users
	for client in clients_object:
		if client.username in blocked_list[sender] or sender in blocked_list[client.username]:
			pass
		else:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				sock.connect((client.ip,client.port))
				sock.sendall(sender + " :: " + message)
				time.sleep(.1)
			except Exception,e:
				print str(e)
			sock.close()

def server_message(message,to):
	global clients_object
	global online_users
	for client in clients_object:
		if client.username == to:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				sock.connect((client.ip,client.port))
				sock.sendall(message)
			except Exception,e:
				print str(e)
			sock.close()

def private_message(message,sender,to):
	global clients_object
	global online_users
	for client in clients_object:
		if client.username == to:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if client.username in online_users:
				try:
					sock.connect((client.ip,client.port))
					sock.sendall(sender +" :: "+ message)
				except Exception,e:
					print str(e)
				sock.close()
			else:
				for client2 in clients_object:
					if client2.username == sender:
						try:
							sock.connect((client2.ip,client2.port))
							sock.sendall(to +" is offline\n"+"Message will be delivered once he is back !! ")
						except Exception,e:
							print str(e)
						sock.close()
				client.mailbox.append(sender +" :: "+ message)
			break


def user_exists(username):
	global clients_credentials
	for credential in clients_credentials:
		if credential[0]==username:
			return True
	return False

def run_client(connection,address):
	global clients_object
	global online_users
	global locked_out_users
	global PORT_NUM
	global clients_credentials
	global blocked_list
	global groups
	msg = connection.recv(RECV_SIZE)
	flag = 1
	answer = ""
	if msg[0:4] == "PORT":
		for client in clients_object:
			if client.port == msg[4:] or str(PORT_NUM) == msg[4:]:
				connection.sendall("NOOK")
				flag = 0
				break
		if flag == 1:
			connection.sendall("OKAY")
	if msg[0:4] == "LOGN":
		tmp_inf = msg.split(" ")
		print "Login request received from "+tmp_inf[1]+":"+tmp_inf[2]
		connection.sendall("NAME"+" Username :: ")
	if msg[0:4] == "NAME":
		username = msg[4:]
		flag = 1
		for client in clients_object:
			if client.username == username:
				#print online_users
				if (username in online_users):
					flag = 1
					answer = "User already logged in !! "
					break
				elif (username in locked_out_users) :
					flag = 1
					answer = "Acoount has been locked out !! Wait for sometime !! "
					break
				else:
					flag = 0
					connection.sendall("KNOW "+str(username in locked_out_users))
				break
		if flag == 1:
			if ((username in online_users) or (username in locked_out_users )):
				connection.sendall("CLOS"+" "+answer)
			else:
				connection.sendall("NOOK"+" User doesn't exist")
	if msg[0:4] == "PASS":
		details = msg.split(" ")
		password = details[0][4:]
		username = details[1][4:]
		user_ip = details[2][4:]
		user_port = details[3][4:]
		attempts = details[4][4:]
		flag = 1
		answer = ""
		for client in clients_object:
			if client.username == username :
				if int(attempts) >= 2 and client.password != password:
					locked_out_users.append(username)
					tmp_thread = threading.Thread(target=unlockuser, args=(client.username,))
					tmp_thread.daemon = True
					tmp_thread.start()
					flag = 1
					answer = "Too many attempts, my friend !! Account Locked !! "
					print "User Account :: " + username + " has been locked out"
					break
				elif client.password == password:
					client.port = int(user_port.strip())
					client.ip = user_ip
					#print client.ip
					#print client.port
					flag = 0
					online_users.append(username)
					last_active[username] = datetime.datetime.now()
					locked_out_users = [item for item in locked_out_users if item != client.username]
					print username + " has logged in !!"
					connection.sendall("OKAY"+" Welcome to Chat Palace !! \nEnter offline to check the offline messages !!")
				else:
					pass
				break
		if flag == 1:
			if username in locked_out_users :
				connection.sendall("CLOS"+" "+answer)
			else:
				connection.sendall("NOOK"+" Username and Password doesn't match !! ")
	if msg[0:4] == "EXIT" :
		online_users = [item for item in online_users if item != msg[4:]]
	if msg[0:4] == "CMND" :
		result = 1
		cmnd = msg.split(" ")
		username = cmnd[1]
		if cmnd[2] == "block" and len(cmnd) == 4:
			if user_exists(cmnd[3]):
				result = 0
				tmp_list = blocked_list[username]
				tmp_list.append(cmnd[3])
				blocked_list[username] = tmp_list
				#print blocked_list
				print cmnd[1] + " has blocked "+cmnd[3]
				answer = "You blocked "+cmnd[3]+" !! User successfully blocked !! " 
			else:
				result = 0
				answer = " User with this name doesn't exist !! "
		elif cmnd[2] == "unblock" and len(cmnd) == 4:
			if user_exists(cmnd[3]):
				result = 0
				tmp_list = blocked_list[username]
				tmp_list = [item for item in tmp_list if item != cmnd[3]]
				blocked_list[username] = tmp_list
				#print blocked_list
				print cmnd[1] + " has unblocked " + cmnd[3]
				answer = "You unblocked "+cmnd[3]+" !! User successfully unblocked !! " 
			else:
				result = 0
				answer = " User with this name doesn't exist !! "
		elif cmnd[2] == "ping" and len(cmnd) == 4:
			receiver = cmnd[3]
			if user_exists(cmnd[3]):
				if (username in blocked_list[receiver]):
					result= 0
					answer = "You can't message ... You are blocked by "+cmnd[3]
				elif (receiver in blocked_list[username]):
					result= 0
					answer = "You can't message .. You have blocked "+cmnd[3]
				else:
					result = 1
					if receiver in online_users:
						result = 0 
						answer = receiver + " is online .... You can message him !!"
					else:
						result = 0
						answer = receiver + " is offline .... You can leave an offline message !!"
			else:
				result = 0
				answer = "User doesn't exist !! "
		elif cmnd[2] == "whoelse" and len(cmnd) == 3:
			result = 0
			answer = "List of Online Users are\n"
			answer = answer + "\n".join(online_users)
		elif cmnd[2] == "grouplist" and len(cmnd) == 3:
			result = 0
			answer = "Groups in which you are in are\n"
			for groupn in groups.keys():
				if cmnd[1] in groups[groupn]:
					gmems = groups[groupn]
					gmems = ' '.join(gmems)
					answer = answer + groupn + " :: " + gmems + "\n"
		elif cmnd[2] == "wholasthr" and len(cmnd) == 3:
			result = 0
			tmp_list = []
			answer = "\nUsers online within an hour\n"
			#print last_active
			for uname in last_active.keys():
				if uname == username:
					pass
				elif last_active[uname] != None:
					current_time = datetime.datetime.now()
					diff = current_time - last_active[uname]
					if diff.seconds/3600 == 0:
						tmp_list.append(uname)

			answer = answer + "\n".join(tmp_list)
		elif cmnd[2] == "create" and cmnd[3]=="group":
			gflag = 1
			if len(cmnd) >= 6:
				group_name = cmnd[4]
				group_members = cmnd[5:]
				group_members.append(cmnd[1])
				for member in group_members:
					if(user_exists(member)):
						pass
					else:
						gflag = 0
						result = 0
						answer = member + " is not a valid user !!"
						break
				if gflag == 1:
					groups[group_name] = group_members
					print group_name + " created with members ::" + ' '.join(group_members)
					result = 0
					answer = "Group " + group_name +" created !! "
			else:
				result = 0
				answer = "Invalid command type !!"
		elif cmnd[2] == "message" and cmnd[3] == "group":
			is_group = 0
			if len(cmnd) >= 6:
				group_name = cmnd[4]
				if group_name in groups.keys():
					message = cmnd[5:]
					message = ' '.join(message)
					result = 1
					group_message(message,group_name,cmnd[1])
				else:
					result = 0
					answer = "No group exists with this name !! "
			else:
				result = 0
				answer = "Invalid command !! "
		elif cmnd[2] == "broadcast" and len(cmnd) >=4:
			result = 1
			message = cmnd[3:]
			print " Broadcast message "+cmnd[1] + " :: " + ' '.join(message)
			broadcast_message(' '.join(message),cmnd[1])
		elif cmnd[2] == "offline" and len(cmnd) == 3:
			result = 1
			for client in clients_object:
				if client.username == cmnd[1]:
					server_message("Offline messages\n",cmnd[1])
					for message in client.mailbox:
						server_message(message,cmnd[1])
					client.mailbox = []
					break
		elif ((cmnd[2] == "message" and cmnd[3] != "group" ) and len(cmnd)>=5):
			receiver = cmnd[3]
			if user_exists(cmnd[3]):
				if (username in blocked_list[receiver]):
					result= 0
					answer = "You are blocked by "+cmnd[3]
				elif (receiver in blocked_list[username]):
					result= 0
					answer = "You can't message..You have blocked "+cmnd[3]
				else:
					result = 1
					message = cmnd[4:]
					private_message(' '.join(message),username,cmnd[3])
					print cmnd[1] + " --> " + cmnd[3] + " " + ' '.join(message)
			else:
				result = 0
				answer = "User doesn't exist !! "
		elif cmnd[2] == "logout":
			result = 0
			logout_user(cmnd[1])
			print cmnd[1] +" has logged out successfully !! "
			answer = "You have been successfully logged out !! "
		else:
			result = 0
			answer = "Incorrect Command Format !! "
		if result == 0:
			#print answer
			#connection.sendall(answer)
			connection.close()
			server_message(answer,username)




def server():
	global clients_credentials
	global clients_object
	global PORT_NUM
	global last_active
	global HOST
	temp = sys.argv
	
	if len(temp) != 2 :                       
		print "Incorrect Format\nPlease enter the command as :: python server.py port_number"
		sys.exit(1)
	else:
		print "Server started successfully !! "
		fname = "clients.txt"
		with open(fname) as f:
			content = f.readlines()
		content = [x.strip() for x in content]
		for credentials in content:
			credentials = credentials.split(" ")
			clients_credentials.append([credentials[0],credentials[1]])
			blocked_list[credentials[0]]=[credentials[0]]
			last_active[credentials[0]] = None

		for user_info in clients_credentials:
			clients_object.append(client(user_info[0],user_info[1]))


		PORT_NUM = int(sys.argv[1])                                     #port number to be used
		                                                                #setting up the connection
		server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	server_sock.bind((HOST, PORT_NUM))
    	server_sock.listen(1)                                           #putting the socket in the server mode

    	main_thread = threading.Thread(name = 'daemon',target = daemon)                       #making it as daemon thread
    	main_thread.setDaemon(True)                                                    
    	main_thread.start()              
    	
    	while True:
        	connection, address = server_sock.accept()
        	new_thread = threading.Thread(target=run_client, args=(connection,address))
        	new_thread.start()



def signal_handler(signal, frame):
        print('You have pressed Ctrl+C!')
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)               #in case of keyboard interrupt 
signal.signal(signal.SIGPIPE, signal.SIG_IGN)              #ignore the signal corresponding to sockets
server()
