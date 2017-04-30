# # load from file:
# with open('/path/to/my_file.json', 'r') as f:
#     try:
#         data = json.load(f)
#     # if the file is empty the ValueError will be thrown
#     except ValueError:
#         data = {}

#!/usr/bin/env python

import socket,sys,time
import json
from thread import *

SERVER_IP = '192.168.100.11'
SERVER_PORT = int(sys.argv[1])
BUFFER_SIZE = 20  # Normally 1024, but a smaller value results in faster response

users_sockets = {}	#user to socket mapping

socketid_name = {}	#socket to user mapping

ip_addr = {}		#name to ip addr mapping	

users = {}			#user to timestamp (last seen or online) mapping

groups_name = []	

group_to_name = {	#group to list of names in group mapping
	'Networks':["kanak","abhishek"]
}

name_to_group = {}	#name to 'groups in which the user is' mapping

loginCred = {		#login credentials database
	"kanak":"kanak",
	"abhishek":"abhishek",
	"shaan":"shaan"
}

chatDatabase = {}	#all chats stored as dictionary of dictionary of lists
					#chatDatabase[user1][user2] returns list of chat messages between them as shown on user1's screen

groupChatDatabase = {}	#group chats, group to list of chat messages mapping

#returns whether user cred valid or not and name of the valid user
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

#function for sending list of users and their timestamps to all users
#when a new user logs in
#when a user logs out
def sendUserList():
	global users, users_sockets
	msg = "list:" + str(users)	#str(dict) converts a dictionary to a string
	print 6,users
	for user in users_sockets:	#send to all online users
		print 1,user
		users_sockets[user].send(msg+"$")	
	time.sleep(1)

#send chat history to newly logged in clients
def sendChatHistory(name):
	global chatDatabase, groupChatDatabase, name_to_group, users_sockets
	msg = "Database:" + str(chatDatabase[name])
	users_sockets[name].send(msg+"$")
	time.sleep(2)
	groupdict = {}
	if name in name_to_group.keys():
		for group in name_to_group[name]:
			groupdict[group] = groupChatDatabase[group]
	msg = "GroupDatabase:" + str(groupdict)
	users_sockets[name].send(msg+"$")
	time.sleep(1)

# dict2 = eval(str1)
##########################################################
# save to file:
	# with open("'"+name+".json'", 'w') as f:
	# 	json.dump(chatDatabase[name], f)

	# users_sockets[name].send()
############################################################

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

		#temp stores the identifier of the message, which decides how to handle the message
		temp = data[:data.find(":")]

		#user wants to login, sends credentials, so check credentials, send chat history and list of live users if successful log in
		if(temp=="login"):
			isvalid,name = validuser(data[data.find(":")+1:])
			if(isvalid):
				users_sockets[name] = conn
				print 22,conn.fileno()
				socketid_name[conn.fileno()] = name
				ip_addr[name] = addr[0]

				users[name] = "Online"
					
				if name in chatDatabase.keys():
					sendChatHistory(name)
				elif name not in chatDatabase.keys():
					chatDatabase[name] = {}
				print "send live users"
				sendUserList()
				
		#message to be sent to a user, handles offline user case by updating chat database
		elif(temp=="msg"):
			print 23,conn.fileno()
			name = socketid_name[conn.fileno()]
			data = data[data.find(":")+1:]
			towhom = data[:data.find(":")]
			message = data[data.find(":")+1:]
			new_msg = "msg:"+name+":"+message
			print name,towhom,message,new_msg
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
			print name,towhom,message,new_msg

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
				
############new group server side handling###########
		# elif(temp=="NewGroup"):
		# 	data = data[data.find(":")+1:]
		# 	groupname = data[:data.find(":")]
		# 	data = data[data.find(":")+1:]
		# 	usersInGroup = data.split(',')
		# 	group_to_name[groupname] = usersInGroup
		# 	users[groupname] = "Group"
		# 	groupChatDatabase[groups_name] = []
		# 	sendUserList()
#######################################################
		#logout, send list of users to other users
		elif(temp=="logout"):
			name = socketid_name[conn.fileno()]
			data = data[data.find(':')+1:]
			users[name] = data
			print data
			del users_sockets[name]
			del socketid_name[conn.fileno()]
			sendUserList()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.setsockopt(socket.SO_REUSEADDR)
s.bind((SERVER_IP, SERVER_PORT))
s.listen(1)

while True:
	conn, addr = s.accept()
	start_new_thread(new_client,(conn,))

conn.close()