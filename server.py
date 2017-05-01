# load from file:

#!/usr/bin/env python

import socket,sys,time
import json
from thread import *
import ldap

SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
BUFFER_SIZE = 20  # Normally 1024, but a smaller value results in faster response

users_sockets = {}	#user to socket mapping

socketid_name = {}	#socket to user mapping

ip_addr = {}		#name to ip addr mapping	

users = {}			#user to timestamp (last seen or online) mapping

group_to_name = {}	#group to list of names in group mapping


name_to_group = {}	#name to 'groups in which the user is' mapping

chatDatabase = {}	#all chats stored as dictionary of dictionary of lists
					#chatDatabase[user1][user2] returns list of chat messages between them as shown on user1's screen

groupChatDatabase = {}	#group chats, group to list of chat messages mapping

#returns whether user cred valid or not and name of the valid user
def validuser(data):
	name = data[:data.find(":")]
	password = data[data.find(":")+1:]
	print name, password
	conn = ldap.open('cs252lab.cse.iitb.ac.in')
	try:
		conn.bind_s("cn="+name+",dc=cs252lab,dc=cse,dc=iitb,dc=ac,dc=in",password)
		return True,name
	except ldap.LDAPError:
		return False,name

#function for sending list of users and their timestamps to all users
#when a new user logs in
#when a user logs out
def sendUserList():
	global users, users_sockets, group_to_name, name_to_group
	msg = "list:" + str(users) + "$" #str(dict) converts a dictionary to a string
	for user in users_sockets:	#send to all online users
		users_sockets[user].send(msg)	
	time.sleep(2)
	for user in users_sockets:	#send to all online users
		msgGroup = "grouplist:{"
		if user in name_to_group.keys():
			for group in name_to_group[user]:
				msgGroup = msgGroup + "\""+str(group)+ "\"" + ":" + str(group_to_name[group]) + ","
			msgGroup = msgGroup + "}$"
			users_sockets[user].send(msgGroup)

#send chat history to newly logged in clients
def sendChatHistory(name):
	global chatDatabase, groupChatDatabase, name_to_group, users_sockets
	msg = "Database:" + str(chatDatabase[name])
	time.sleep(1)
	users_sockets[name].send(msg+"$")
	time.sleep(1)
	groupdict = {}
	if name in name_to_group.keys():
		for group in name_to_group[name]:
			groupdict[group] = groupChatDatabase[group]
	msg = "GroupDatabase:" + str(groupdict)
	users_sockets[name].send(msg+"$")

def updateDatabase():
	with open('chatDatabase.json', 'w') as f:
		json.dump(chatDatabase, f)
	with open('groupChatDatabase.json', 'w') as f:
		json.dump(groupChatDatabase, f)
	with open('users.json', 'w') as f:
		json.dump(users, f)
	with open('name_to_group.json', 'w') as f:
		json.dump(name_to_group, f)
	with open('group_to_name.json', 'w') as f:
		json.dump(group_to_name, f)

#function defining how to handle the various messages from the client
def new_client(conn):
	global chatDatabase, groupChatDatabase, name_to_group, group_to_name, users_sockets, users
	while True:
		#the code below adds up the messages until a $ is observed
		data =""
		while True:
			data = data + conn.recv(BUFFER_SIZE)
			if(len(data)!=0):
				if(data[-1]=="$"):
					break

		print 0,data
		data = data[:-1]
		tags = ["PyQt4.QtCore.QString(u",")"]
		for tag in tags:
			data = data.replace(tag,'')
		#temp stores the identifier of the message, which decides how to handle the message
		temp = data[:data.find(":")]

		#user wants to login, sends credentials, so check credentials, send chat history and list of live users if successful log in
		if(temp=="login"):
			isvalid,name = validuser(data[data.find(":")+1:])
			loginMsg = "login:" + str(isvalid) + "$"
			conn.send(loginMsg)
			time.sleep(1)
			if(isvalid):
				users_sockets[name] = conn
				socketid_name[conn.fileno()] = name
				ip_addr[name] = addr[0]

				users[name] = "Online"
					
				sendUserList()
				if name in chatDatabase.keys():
					sendChatHistory(name)
				elif name in name_to_group.keys():
					sendChatHistory(name)
				else:
					chatDatabase[name] = {}
				
		#message to be sent to a user, handles offline user case by updating chat database
		elif(temp=="msg"):
			name = socketid_name[conn.fileno()]
			data = data[data.find(":")+1:]
			towhom = data[:data.find(":")]
			message = data[data.find(":")+1:]
			new_msg = "msg:"+name+":"+message
			if towhom in users.keys():
				if users[towhom] == "Online":
					users_sockets[towhom].send(new_msg+"$")
				msg = "You: " + message
				msg_towhom = name + ": "+ message 
				if towhom in chatDatabase[name].keys():
					chatDatabase[name][towhom].append(msg)
				else:
					chatDatabase[name][towhom] = [msg]
				if name in chatDatabase[towhom].keys():
					chatDatabase[towhom][name].append(msg_towhom)
				else:
					chatDatabase[towhom][name] = [msg_towhom]
			else:
				msg = "error:Delivery Fail"
				conn.send(msg)

		#message to be sent to a group, ignores if any user online, updates group chat database
		elif(temp=="group"):
			name = socketid_name[conn.fileno()]
			data = data[data.find(":")+1:]
			towhom = data[:data.find(":")]
			message = data[data.find(":")+1:]
			new_msg = "group:"+towhom+":"+name+":"+message

			if towhom in groupChatDatabase.keys():
				groupChatDatabase[towhom].append(name + ": " + message)
			else:
				groupChatDatabase[towhom] = [name + ": " + message]
				
			if towhom in group_to_name.keys():
				for user in group_to_name[towhom]:
					if user!=name:
						try:
							users_sockets[user].send(new_msg+"$")
						except Exception,e:
							pass
			else:
				msg = "error:Delivery Fail"
				conn.send(msg+"$")
				
		elif(temp=="NewGroup"):
			data = data[data.find(":")+1:]
			groupname = data[:data.find(":")]
			data = data[data.find(":")+1:]
			usersInGroup = eval(data)
			if groupname not in group_to_name.keys():
				group_to_name[groupname] = usersInGroup
				for user in usersInGroup:
					if user in name_to_group.keys():
						name_to_group[user].append(groupname)
					else:
						name_to_group[user] = [groupname]
				groupChatDatabase[groupname] = []
			sendUserList()

		#logout, send list of users to other users
		elif(temp=="logout"):
			name = socketid_name[conn.fileno()]
			data = data[data.find(':')+1:]
			users[name] = data
			del users_sockets[name]
			del socketid_name[conn.fileno()]
			sendUserList()

		updateDatabase()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setsockopt(socket.SO_REUSEADDR)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(1)

try:
	with open('chatDatabase.json', 'r') as f:
		chatDatabase = json.load(f)
except IOError:
	data = {}

try:
	with open('chatDatabase.json', 'r') as f:
		groupChatDatabase = json.load(f)
except IOError:
	groupChatDatabase = {}

try:
	with open('users.json', 'r') as f:
		users = json.load(f)
except IOError:
	users = {}

try:
	with open('group_to_name.json', 'r') as f:
		group_to_name = json.load(f)
except IOError:
	group_to_name = {}

try:
	with open('name_to_group.json', 'r') as f:
		name_to_group = json.load(f)
except IOError:
	name_to_group = {}

while True:
	conn, addr = s.accept()
	start_new_thread(new_client,(conn,))
