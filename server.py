#!/usr/bin/env python

import socket,sys,time
from thread import *

SERVER_IP = '10.196.5.108'
SERVER_PORT = int(sys.argv[1])
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

users_sockets = {}
socketid_name = {}
ip_addr = {}
live_users = []
groups_name = []
x = ["kanak","abhishek"]
groups = {
	'Networks':x
}
loginCred = {
	"kanak":"kanak",
	"abhishek":"abhishek",
	"shaan":"shaan"
}


#return name of valid user and a bool telling whether valid or not
def validuser(data):
	print data
	name = data[:data.find(":")]
	password = data[data.find(":")+1:]
	try:
		if(loginCred[name] != password):
			return False,name
		return True,name
	except Exception,e:
		return False,name

def sendliveusers():
	global live_users,users_sockets
	msg = ":".join(live_users)
	for user in live_users:
		print 1,user
		users_sockets[user].send("list:"+msg)
	time.sleep(1)

def new_client(conn):
	while True:
		data =""
		while True:
			data = data + conn.recv(BUFFER_SIZE)
			print data
			print data[-1]
			if(data[-1]=="$"):
				break
		print 0,data
		data = data[:-1]
		temp = data[:data.find(":")]
		b = "msg"
		print -1,temp,type(temp),temp == "login"
		if(temp=="login"):
			# print 23,temp
			isvalid,name = validuser(data[data.find(":")+1:])
			if(isvalid):
				users_sockets[name] = conn
				print 22,conn.fileno()
				socketid_name[conn.fileno()] = name
				ip_addr[name] = addr[0]
				if name not in live_users:
					live_users.append(name)
				sendliveusers()
				
		elif(temp=="msg"):
			print 23,conn.fileno()
			name = socketid_name[conn.fileno()]
			data = data[data.find(":")+1:]
			towhom = data[:data.find(":")]
			message = data[data.find(":")+1:]
			new_msg = "msg:"+name+":"+message
			print name,towhom,message,new_msg
			if towhom in live_users:
				users_sockets[towhom].send(new_msg)
			else:
				msg = "error:Delivery Fail"
				conn.send(msg)
		elif(temp=="group"):
			name = socketid_name[conn.fileno()]
			data = data[data.find(":")+1:]
			towhom = data[:data.find(":")]
			message = data[data.find(":")+1:]
			new_msg = "group:"+towhom+":"+name+":"+message
			print name,towhom,message,new_msg
			if towhom in groups.keys():
				for user in groups[towhom]:
					if user!=name:
						try:
							users_sockets[user].send(new_msg)
						except Exception,e:
							pass
			else:
				msg = "error:Delivery Fail"
				conn.send(msg)
		elif(temp=="logout"):
			name = socketid_name[conn.fileno()]
			live_users.remove(name)
			del users_sockets[name]
			del socketid_name[conn.fileno()]
			sendliveusers()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setsockopt(socket.SO_REUSEADDR)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(1)

while True:
	conn, addr = s.accept()
	start_new_thread(new_client,(conn,))

conn.close()