import sys,os
import socket,signal,os,time,random
from multiprocessing import Lock
import threading

lock = Lock()
HOST_IP = ""
RECV_SIZE = 1024
PORT = ""
username = ""


def exit_update(username):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((HOST_IP, PORT))
	client_socket.sendall("EXIT"+username)


def serve_client(connection):
    global lock
    #print "The message"
    message = connection.recv(RECV_SIZE)
    #sys.exit(0)
    #print "chat---" + message
    lock.acquire()
    try:
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    finally:
        lock.release()

	connection.close()
	return(0)


def listener_thread(client_sock):
	while True:
		#print "repeat !! "
		#time.sleep(4)
		try:
			conn, addr = client_sock.accept()
			server = threading.Thread(target=serve_client, args=(conn,))
			server.start()
		except Exception:
			print Exception



def client_fun():
	global lock
	global username
	global HOST_IP
	global PORT 
	global RECV_SIZE
	temp = sys.argv
	if len(temp) != 3:
	        print 'Wrong Format\nPlease Enter as :: python client.py host_ip port_number'
	        sys.exit(1)
	else:
		bind_var = ""
		PORT = int(sys.argv[2])
		HOST_IP = sys.argv[1]
		client_ip = socket.gethostbyname(socket.gethostname())
		port_to_bind = random.randint(1100, 65000)
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((HOST_IP, PORT))
		while 1:
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.connect((HOST_IP, PORT))
			client_socket.sendall("PORT"+str(port_to_bind))
			msg = client_socket.recv(RECV_SIZE)
			if msg == "NOOK":
				port_to_bind = random.randint(1100, 65000)
			else:
				bind_var = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				bind_var.bind((client_ip, port_to_bind))
				bind_var.listen(1)
				break
		try:
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.connect((HOST_IP, PORT))
			client_socket.sendall("LOGN "+client_ip+" "+str(port_to_bind))
		except Exception:
			print 'Error Occurred !! '

		msg = client_socket.recv(RECV_SIZE)
		
		if msg[0:4] == "NAME":
			while 1:
				username = raw_input(">> " + "Username :: ")
				if username != "" :
					client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					client_socket.connect((HOST_IP, PORT))
					client_socket.sendall("NAME"+username)
					msg = client_socket.recv(RECV_SIZE)
					if msg[0:4] == "NOOK":
						print msg[4:]
					elif msg[0:4] == "CLOS":
						client_socket.close()
						print msg[4:]
						exit_update(username)
						sys.exit(0)
					else:
						break
		if msg[0:4] == "KNOW":
			attempts = 0
			while 1:
				password = raw_input(">> " + "Password :: ")
				if password != "":
					client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					client_socket.connect((HOST_IP, PORT))
					client_socket.sendall("PASS"+password+" USER"+username+ " IPAD" + client_ip +" PORT"+str(port_to_bind)+" ATMP"+str(attempts))
					msg = client_socket.recv(RECV_SIZE)
					if msg[0:4] == "NOOK":
						attempts = attempts + 1
						print msg[4:]
					elif msg[0:4] == "CLOS":
						client_socket.close()
						print msg[4:]
						exit_update(username)
						sys.exit(0)
						break
					else:
						print "Authenticated Successfully !! "
						break


		listener = threading.Thread(target=listener_thread, args=(bind_var,))
		listener.daemon = True
		listener.start()
		description = ""
		
		while True:
			lock.acquire()
			try:
				#sys.stdout.write(description + '\n')
				sys.stdout.flush()
			finally:
				lock.release()

			user_cmnd = raw_input();
			if user_cmnd != "":
				client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				client_socket.connect((HOST_IP, PORT))
				client_socket.sendall("CMND "+ username + " " + user_cmnd)
				#description = client_socket.recv(RECV_SIZE)
				#print "Check it"

			client_socket.close()
			if user_cmnd == "logout":
				sys.exit(0)

def signal_handler(signal, frame):
		global HOST_IP
		global PORT
		print('You have pressed Ctrl+C!\nYou have been successfully logged out !')
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((HOST_IP, PORT))
		client_socket.sendall("CMND "+ username + " logout")
		description = client_socket.recv(RECV_SIZE)
		sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)               #in case of keyboard interrupt 
signal.signal(signal.SIGPIPE, signal.SIG_IGN)              #ignore the signal corresponding to sockets
client_fun()

