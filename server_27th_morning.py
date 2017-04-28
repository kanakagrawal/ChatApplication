#!/usr/bin/env python

import socket,sys,time
from thread import *

SERVER_IP = '192.168.100.17'
SERVER_PORT = int(sys.argv[1])
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

users_sockets = {}
socketid_name = {}
ip_addr = {}
live_users = []
groups_name = []
x = ["kanak","abhishek"]
group = {
	'Networks':x
}
loginCred = {
	"kanak":"kanak",
	"abhishek":"abhishek"
}

def display_online_users(name):
	global users_sockets,live_users	
	conn = users_sockets[name]
	for a in live_users:
		conn.send(a+"\n")
	conn.send("\n")

def talk(name):
	global users_sockets,live_users	
	conn = users_sockets[name]
	data = "Enter your message\n"
	conn.send(data)  # echo
	while True:
		time.sleep(1)
		data = "input_needed"
		conn.send(data)  # echo
		msg = conn.recv(BUFFER_SIZE)
		peer_conn = users_sockets[talkingto[name]]
		peer_conn.send(name+": "+msg)

def talk_with_someone(name):
	global users_sockets,live_users	
	conn = users_sockets[name]
	data = "Whom would you like to talk to?\n"
	conn.send(data)  # echo
	data = "Please tell the name\n"
	conn.send(data)  # echo
	time.sleep(1)
	data = "input_needed"
	conn.send(data)  # echo
	nametotalk = conn.recv(BUFFER_SIZE)
	talkingto[name] = nametotalk
	talk(name)

def group_talk(name, grp_to_connect):
	global users_sockets,live_users	
	conn = users_sockets[name]
	data = "Enter your message\n"
	conn.send(data)  # echo
	while True:
		time.sleep(1)
		data = "input_needed"
		conn.send(data)  # echo
		msg = conn.recv(BUFFER_SIZE)
		for peers in mem[grp_to_connect]:
			if peers != name:
				peer_conn = users_sockets[peers]
				peer_conn.send(name+": "+msg)

def group_chat(name):
	global users_sockets,live_users
	conn = users_sockets[name]
	data = "Which chat would you like to join?\n"
	conn.send(data)
	time.sleep(1)
	data = "input_needed"
	conn.send(data)
	grp_to_connect = conn.recv(BUFFER_SIZE)
	mem[grp_to_connect].append(name)
	group_talk(name, grp_to_connect)


def user_options(name):
	global users_sockets,live_users	
	conn = users_sockets[name]
	data = "Select one of the following\n"
	conn.send(data)  # echo
	data = "1 - View all online\n"
	conn.send(data)  # echo
	data = "2 - Talk with someone\n"
	conn.send(data)  # echo
	data = "3 - Group Chat\n"
	conn.send(data)
	data = "4 - Logout\n"
	conn.send(data)  # echo
	time.sleep(1)
	data = "input_needed"
	conn.send(data)  # echo
	action = int(conn.recv(BUFFER_SIZE))
	print action
	if(action==1):						##View all online
		display_online_users(name)
		user_options(name)
	elif(action==2):					##Talk with someone
		talk_with_someone(name)
	elif(action==3):
		group_chat(name)
	elif(action==4):
		data = "closecloseclose"
		conn.send(data)  # echo
		time.sleep(1)
		conn.close()
		del users_sockets[name]

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

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setsockopt(socket.SO_REUSEADDR)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(1)

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
			elif towhom in groups_name:
				for user in group[towhom]:
					try:
						users_sockets[user].send(new_msg)
					except Exception,e:
						pass
			else:
				msg = "error:Delivery Fail"
				conn.send(msg)
		# elif(temp=="group"):

		elif(temp=="logout"):
			name = socketid_name[conn.fileno()]
			live_users.remove(name)
			del users_sockets[name]
			del socketid_name[conn.fileno()]
			sendliveusers()

while True:
	conn, addr = s.accept()
	start_new_thread(new_client,(conn,))

conn.close()