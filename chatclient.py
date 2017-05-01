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

authenticated = False


TCP_IP = sys.argv[1]
TCP_PORT = int(sys.argv[2])
BUFFER_SIZE = 50


def sendInfoToServer(name,s):
	global groups
	grouplist = groups[str(name)]
	grouplist.append(username)
	# msg = ""
	grouplist = str(grouplist)
	x = "msg = \"NewGroup:"+name+":"+grouplist+"$\""
	exec(str(x))

	s.send(msg)

def sendmessage(currentUser,msg,s):
	global groups
	new_msg = ""
	if currentUser in groups.keys():
		x = "new_msg = \"group:"+currentUser+":"+msg+"$\""
		exec(str(x))
	else:
		x = "new_msg = \"msg:"+currentUser+":"+msg+"$\""
		exec(str(x))
		
	sent = s.send(new_msg)

	time.sleep(2)

class GUI_refresh(QThread):

	received = pyqtSignal()

	def __init__(self, parent = None):

		QThread.__init__(self, parent)

	def __del__(self):
		self.exiting = True
		self.wait()

	def run(self):
		while True:
			self.sleep(3) 
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

		self.ui.pushButton.clicked.connect(partial(self.sendChat))
		self.ui.pushButton_2.clicked.connect(partial(self.logout))
		self.ui.pushButton_3.clicked.connect(partial(self.createGroup))

	def createGroup(self):
		global users, groupChatDatabase
		for user in users.keys():
			exec("self.ui.checkbox_"+user+" = QCheckBox('"+user+"')")
			exec("self.ui.checkbox_"+user+".stateChanged.connect(partial(self.btnstate,user))")
			exec("self.ui.verticalLayout.addWidget(self.ui.checkbox_"+user+")")
		self.ui.textEdit_2 = QTextEdit(self.ui.verticalLayoutWidget)
		self.ui.textEdit_2.setObjectName(_fromUtf8("textEdit_2"))
		self.ui.verticalLayout.addWidget(self.ui.textEdit_2)
		# self.ui.textEdit_2.setText("Name your group")	
		self.ui.submitGroup = QPushButton(self.ui.verticalLayoutWidget)
		self.ui.submitGroup.setObjectName(_fromUtf8('submitGroup'))
		self.ui.verticalLayout.addWidget(self.ui.submitGroup)
		self.ui.submitGroup.setText("Submit")
		self.ui.submitGroup.clicked.connect(partial(self.submitGroup))

	def submitGroup(self):
		global temporaryGroupList, users, groups, currentUser, groupChatDatabase
		if len(temporaryGroupList)!=0:
			name = self.ui.textEdit_2.toPlainText()
			name.replace(' ', '_')
			self.ui.textEdit_2.setPlainText("")
			if name not in groupChatDatabase.keys():
				groups[str(name)] = temporaryGroupList
				sendInfoToServer(name,self.s)
			else:
				print "Group name already exists"
			for user in users.keys():
				exec("self.ui.checkbox_"+user+".setParent(None)")
				exec("self.ui.textEdit_2.setParent(None)")
				exec("self.ui.submitGroup.setParent(None)")


		temporaryGroupList = []
		self.showcurrentchat(currentUser)

	def btnstate(self, user):
		exec("ischecked = self.ui.checkbox_"+user+".isChecked()")
		if ischecked == True:
			temporaryGroupList.append(user)
		else:
			temporaryGroupList.remove(user)

	def logout(self):
		msg = "logout:"
		timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		self.s.send(msg+timestamp+"$")
		time.sleep(1)
		sys.exit(0)

	def sendChat(self):
		global currentUser, chatDatabase, groupChatDatabase
		msg = self.ui.textEdit.toPlainText()
		self.ui.textEdit.setPlainText("")
		if(msg!=""):
			sendmessage(currentUser,msg,self.s)
			if currentUser not in groups.keys():
				if currentUser not in chatDatabase.keys():
					x = ["You: "+msg]
					chatDatabase[currentUser] = x
				else:
					chatDatabase[currentUser].append("You: "+msg)
			else:
				if currentUser not in groupChatDatabase.keys():
					x = [str("You: "+msg)]
					groupChatDatabase[currentUser] = x
				else:
					groupChatDatabase[currentUser].append(str("You: "+msg))
		self.updateUi()
		

	def showcurrentchat(self,user):
		global currentUser, chatDatabase, groupChatDatabase, users
		currentUser = user
		if user in users.keys():
			if users[user] != "Online":
				label = user + " Last seen " + users[user]
			else:
				label = user + " " + users[user]
		else:
			label = user
		self.ui.label_3.setText(label)
		
		self.ui.listWidget_2.clear()
		if user in chatDatabase.keys():
			for chat in chatDatabase[user]:
				item = QListWidgetItem(chat)
				self.ui.listWidget_2.addItem(item)
		elif user in groupChatDatabase.keys():
			for chat in groupChatDatabase[user]:
				item = QListWidgetItem(chat)
				self.ui.listWidget_2.addItem(item)

	def updateUi(self):
		global users, groups
		self.ui.verticalLayout_2.setAlignment(Qt.AlignTop)
		
		for i in reversed(range(self.ui.verticalLayout_2.count())):
			self.ui.verticalLayout_2.itemAt(i).widget().deleteLater()

		for user in users.keys():
			exec("self.ui.button_"+user+" = QPushButton(self.ui.verticalLayoutWidget_2)")
			exec("self.ui.button_"+user+".setObjectName(_fromUtf8('button_"+user+"'))")
			exec("self.ui.verticalLayout_2.addWidget(self.ui.button_"+user+")")
			exec("self.ui.button_"+user+".setText(user)")
		if len(users.keys())!=0:
			self.showcurrentchat(currentUser)
		
		for user in users.keys():
			exec("self.ui.button_"+user+".clicked.connect(partial(self.showcurrentchat,user))")
		
		for group in groups.keys():
			exec("self.ui.button_"+group+" = QPushButton(self.ui.verticalLayoutWidget_2)")
			exec("self.ui.button_"+group+".setObjectName(_fromUtf8('button_"+group+"'))")
			exec("self.ui.verticalLayout_2.addWidget(self.ui.button_"+group+")")
			exec("self.ui.button_"+group+".setText(group)")
		for group in groups.keys():
			exec("self.ui.button_"+group+".clicked.connect(partial(self.showcurrentchat,group))")	

		if len(users.keys())!=0:
			self.showcurrentchat(currentUser)

	def closeEvent(self, event):
		self.logout()
		event.accept() 


def func(oper):
	global users, groups, username, chatDatabase, groupChatDatabase, currentUser, authenticated
	while(True):
		if(oper=="recv"):
			data = ""
			while True:
				data = data + s.recv(BUFFER_SIZE)
				if(data[-1]=="$"):
					break
			data = data[:-1]
			tags = ["PyQt4.QtCore.QString(u",")"]
			for tag in tags:
				data = data.replace(tag,'')
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
			elif(temp=='group'):
				data = data[data.find(":")+1:]
				fromwhichgroup = data[:data.find(":")]
				data = data[data.find(":")+1:]
				fromwhom = data[:data.find(":")]
				message = data[data.find(":")+1:]
				message = fromwhom+": "+message
				if fromwhichgroup not in groupChatDatabase.keys():
					groupChatDatabase[fromwhichgroup] = [str(message)]
				else:
					groupChatDatabase[fromwhichgroup].append(str(message))
			elif(temp=="list"):
				data = data[data.find(":")+1:]
				users = eval(data)
				del users[username]
				if currentUser=="":
					if len(users.keys())!=0:
						currentUser = users.keys()[0]
			elif(temp=="grouplist"):
				data = data[data.find(":")+1:]
				groups = eval(data)
			elif(temp=='Database'):
				data = data[data.find(":")+1:]
				chatDatabase = eval(data)
			elif(temp=='GroupDatabase'):
				data = data[data.find(":")+1:]
				groupChatDatabase = eval(data)
			elif(temp=='login'):
				data = data[data.find(":")+1:]
				if(data == "False"):
					authenticated = False
				elif(data == "True"):
					authenticated = True
	s.close()


if __name__ == '__main__':
	global s
	username = sys.argv[3]
	password = sys.argv[4]
	MESSAGE = "login:"+username+":"+password+"$"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((TCP_IP, TCP_PORT))
	
	s.send(MESSAGE)
	# time.sleep(1)
	app = QApplication(sys.argv)
	# login = Login(s)

	data = "send"
	start_new_thread(func,(data,))
	data = "recv"
	start_new_thread(func,(data,))


	if authenticated == False:
		time.sleep(2)
	if authenticated == False:
		print "Incorrect Credentials"
	else:
		ui = Ui_MainWindow()
		window = GUI(ui,s)
		window.show()
		app.exec_()

################################################################################
#login window tried but did not work

# class Login(QDialog):

# 	def __init__(self,s, parent=None):
# 		super(Login, self).__init__(parent)
# 		self.s = s
# 		self.textName = QLineEdit(self)
# 		self.textPass = QLineEdit(self)
# 		self.buttonLogin = QPushButton('Login', self)
# 		self.buttonLogin.clicked.connect(self.handleLogin)

# 		layout = QVBoxLayout(self)
# 		layout.addWidget(self.textName)
# 		layout.addWidget(self.textPass)
# 		layout.addWidget(self.buttonLogin)

# 	def handleLogin(self):
# 		global authenticated,username
# 		username = self.textName.text()
# 		x = "loginMsg = \"login:"+self.textName.text()+":"+self.textPass.text()+"$\""
# 		exec(str(x))
		
# 		# loginMsg = "login:"+self.textName.text()+":"+self.textPass.text()+"$"
# 		# print loginMsg
# 		self.s.send(loginMsg)
# 		# print username


# 		# data = ""
# 		# while True:
# 		time.sleep(2)
		
# 	# def updateUi(self, authenticated):
# 	# 	print 1231312321
		

################################################################################