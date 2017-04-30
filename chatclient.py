#!/usr/bin/env python

import socket,sys
from thread import start_new_thread
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from output import Ui_MainWindow
from functools import partial
import time
from time import gmtime, strftime
try:
	_fromUtf8 = QString.fromUtf8

except AttributeError:
	def _fromUtf8(s):
		return s

temporaryGroupList = []

username = ""
users = {}

groups = {}

currentUser = ""

chatDatabase = {}
groupChatDatabase = {}

TCP_IP = '192.168.100.11'
TCP_PORT = int(sys.argv[1])
BUFFER_SIZE = 50

SHOW=False

#######################new group send info to server#####
def sendInfotoServer(name):
	global groups
	grouplist = groups[name]
	grouplist.append(username)
	msg = "NewGroup:"+name+":"
	for a in grouplist:
		msg = msg + a + ","
	s.send(msg+"$")
#########################################################
def sendmessage(currentUser,msg,s):
	global groups
	if currentUser in groups.keys():
		x = "new_msg = \"group:"+currentUser+":"+msg+"$\""
		exec(str(x))
	else:
		x = "new_msg = \"msg:"+currentUser+":"+msg+"$\""
		exec(str(x))
		
	# new_msg = "login:"+currentUser+":"+msg+"\\"
	sent = s.send(new_msg)
	# return sent
	time.sleep(1)
	print "Sent"

class GUI_refresh(QThread):

	received = pyqtSignal()

	def __init__(self, parent = None):

		QThread.__init__(self, parent)

	def __del__(self):
		self.exiting = True
		self.wait()

	def run(self):
		while True:
			self.sleep(3) # this would be replaced by real code, producing the new text...
			self.received.emit()

class GUI(QMainWindow):

	def __init__(self,ui,s,parent=None):
		QMainWindow.__init__(self,	parent)
		self.ui = ui
		self.s = s
		self.ui.setupUi(self)

		self.thread = GUI_refresh()
		self.thread.received.connect(self.updateUi)
		self.thread.start()	

		# self.connect(self.ui.pushButton, SIGNAL('clicked()'), self.sendChat)
		self.ui.pushButton.clicked.connect(partial(self.sendChat))
		self.ui.pushButton_2.clicked.connect(partial(self.logout))
		self.ui.pushButton_2.clicked.connect(partial(self.createGroup))

	def createGroup(self):
		print "hi"
##################code for group creation below, requires testing, define sendInfotoServer######################
#######################################################################################
	# 	global users, groupChatDatabase
	# 	for user in users.keys() and not in groupChatDatabase.keys():
	# 		exec("self.ui.checkbox_"+user+" = QCheckBox('"+user+"')")
	# 		exec("self.ui.checkbox_"+user+".stateChanged.connect(lambda:self.btnstate(self.ui.checkbox_"+user+","+user+"))")
	# 		exec("self.ui.verticalLayout.addWidget(self.ui.checkbox_"+user+")")
	# 	self.ui.textEdit_2 = QtGui.QTextEdit(self.ui.verticalLayoutWidget)
	# 	self.ui.textEdit_2.setObjectName(_fromUtf8("textEdit_2"))
	# 	self.ui.verticalLayout.addWidget(self.ui.textEdit_2)
	# 	self.ui.textEdit_2.setText("Name your group")	
	# 	self.ui.submitGroup = QPushButton(self.ui.verticalLayoutWidget)
	# 	self.ui.submitGroup(_fromUtf8('submitGroup'))
	# 	self.ui.verticalLayout.addWidget(self.ui.submitGroup)
	# 	self.ui.submitGroup.setText("Submit")
	# 	self.ui.submitGroup.clicked.connect(partial(self.submitGroup))

	# def submitGroup(self):
	# 	if len(temporaryGroupList)!=0:
	# 		name = self.ui.textEdit_2.toPlainText()
	# 		self.ui.textEdit.setPlainText("")
	# 		if name not in groupChatDatabase.keys():
	# 			groups[name] = temporaryGroupList
	# 			users[name] = "Online"
	# 			sendInfoToServer(name)
	# 		else:
	# 			print "group name already exists"	
	# 	temporaryGroupList = []
	# 	self.showcurrentchat(currentUser)

	# def btnstate(self, b, user)
	# 	name = b.text()
	# 	if b.isChecked() == True:
	# 		temporaryGroupList.append(user)
	# 	else:
	# 		temporaryGroupList.remove(user)
####################################################

	def logout(self):
		msg = "logout:"
		timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		print timestamp
		self.s.send(msg+timestamp+"$")
		time.sleep(1)
		sys.exit(0)

	def sendChat(self):
		global currentUser, chatDatabase
		msg = self.ui.textEdit.toPlainText()
		self.ui.textEdit.setPlainText("")
		if(msg!=""):
			sendmessage(currentUser,msg,self.s)
			if currentUser not in chatDatabase.keys():
				x = ["You: "+msg]
				chatDatabase[currentUser] = x
			else:
				chatDatabase[currentUser].append("You: "+msg)
		
		self.updateUi()

		# x = "new_msg = \"login:"+currentUser+":"+msg+"$\""
		# exec(str(x))
		# new_msg = "login:"+currentUser+":"+msg+"$"
		# print new_msg
		# new_msg = "login:currentUser:msg\\"

		# self.s.send(new_msg)
		# time.sleep(1)
		# print "Sent"

		

	def showcurrentchat(self,user):
		# new_msg = "login:"+"currentUser"+":"+"msg"+"\\"
		# self.s.send(new_msg)
		# time.sleep(1)
		# print "Sent"
		# exec("self.ui.button_"+user+".setText(_translate("+MainWindow+", "<html><head/><body><p><span style=\"font-weight:600;\">Online Friends</span></p></body></html>", None))")

		# self.ui..setText(_translate("MainWindow", "<html><head/><body><p><span style=\"font-weight:600;\">Online Friends</span></p></body></html>", None))
		global currentUser, chatDatabase, groupChatDatabase, users
		currentUser = user
		if users[user] != "Online":
			label = user + " Last seen " + users[user]
		else:
			label = user + " " + users[user]
		self.ui.label_3.setText(label)
		self.ui.listWidget_2.clear()
		# for i in reversed(range(self.ui.verticalLayout_2.count())):
		# self.ui.verticalLayout_2.itemAt(i).widget().deleteLater()
		if user in chatDatabase.keys():
			for chat in chatDatabase[user]:
				print 5,chat
				item = QListWidgetItem(chat)
				self.ui.listWidget_2.addItem(item)
		elif user in groupChatDatabase.keys():
			for chat in groupChatDatabase[user]:
				item = QListWidgetItem(chat)
				self.ui.listWidget_2.addItem(item)

	def updateUi(self):
		print "called"
		for i in reversed(range(self.ui.verticalLayout_2.count())):
			self.ui.verticalLayout_2.itemAt(i).widget().deleteLater()

		global users, groups
		print 1,users
		for user in users.keys():
			exec("self.ui.button_"+user+" = QPushButton(self.ui.verticalLayoutWidget_2)")
			exec("self.ui.button_"+user+".setObjectName(_fromUtf8('button_"+user+"'))")
			exec("self.ui.verticalLayout_2.addWidget(self.ui.button_"+user+")")
			exec("self.ui.button_"+user+".setText(user)")
		# self.ui.button_Kanak.clicked.connect(lambda : self.showcurrentchat("Kanak"))
		self.showcurrentchat(currentUser)
		
		for user in users.keys():
			exec("self.ui.button_"+user+".clicked.connect(partial(self.showcurrentchat,user))")
		
		for group in groups.keys():
			exec("self.ui.button_"+group+" = QPushButton(self.ui.verticalLayoutWidget_2)")
			exec("self.ui.button_"+group+".setObjectName(_fromUtf8('button_"+group+"'))")
			exec("self.ui.verticalLayout_2.addWidget(self.ui.button_"+group+")")
			exec("self.ui.button_"+group+".setText(group)")
		# self.ui.button_Kanak.clicked.connect(lambda : self.showcurrentchat("Kanak"))
		for group in groups.keys():
			exec("self.ui.button_"+group+".clicked.connect(partial(self.showcurrentchat,group))")	

		self.showcurrentchat(currentUser)
		# exec("self.connect(self.ui.button_"+user+", SIGNAL('clicked()'), self.showcurrentchat)")


		# self.ui.p2 = QPushButton(self.ui.verticalLayoutWidget_2)
		# self.ui.p2.setObjectName(_fromUtf8("p2"))
		# self.ui.verticalLayout_2.addWidget(self.ui.p2)
		# self.ui.p2.setText("Kanak2")

################################################################################

def func(oper):
	global send,check,users,SHOW,username, chatDatabase, groupChatDatabase, currentUser
	# print oper
	while(True):
		if(oper == "send" and send):
			x = raw_input()
			s.send(x)
			send = False
		elif(oper=="recv"):
			data = ""
			while True:
				data = data + s.recv(BUFFER_SIZE)
				if(data[-1]=="$"):
					break
			data = data[:-1]
			print "data",data
			temp = data[:data.find(":")]
			if(temp=="msg"):
				data = data[data.find(":")+1:]
				fromwhom = data[:data.find(":")]
				message = data[data.find(":")+1:]
				message = fromwhom+": "+message
				if fromwhom not in chatDatabase.keys():
					chatDatabase[fromwhom] = [message]
				else:
					chatDatabase[fromwhom].append(message)
				print "chatDatabase",chatDatabase
				SHOW = True
			elif(temp=="list"):
				data = data[data.find(":")+1:]
				users = eval(data)
				del users[username]
				if currentUser=="":
					currentUser = users.keys()[0]	
				SHOW = True
			elif(temp=='group'):
				data = data[data.find(":")+1:]
				fromwhichgroup = data[:data.find(":")]
				data = data[data.find(":")+1:]
				fromwhom = data[:data.find(":")]
				message = data[data.find(":")+1:]
				message = fromwhom+": "+message
				if fromwhichgroup not in groupChatDatabase.keys():
					groupChatDatabase[fromwhichgroup] = [message]
				else:
					groupChatDatabase[fromwhichgroup].append(message)
				SHOW = True
			elif(temp=='Database'):
				data = data[data.find(":")+1:]
				chatDatabase = eval(data)
				SHOW = True
			elif(temp=='GroupDatabase'):
				data = data[data.find(":")+1:]
				groupChatDatabase = eval(data)
				SHOW = True
	s.close()


if __name__ == '__main__':
	username = sys.argv[2]
	password = sys.argv[3]
	MESSAGE = "login:"+username+":"+password+"$"
	check = True
	send = False
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	
	s.send(MESSAGE)
	time.sleep(1)

	data = "send"
	start_new_thread(func,(data,))
	data = "recv"
	start_new_thread(func,(data,))

	print "received data:", data

	app = QApplication(sys.argv)
	ui = Ui_MainWindow()
	window = GUI(ui,s)
	window.show()
	app.exec_()
