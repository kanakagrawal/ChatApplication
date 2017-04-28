#!/usr/bin/env python

import socket,sys
from thread import start_new_thread
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from output import Ui_MainWindow
from functools import partial
import time

try:
	_fromUtf8 = QString.fromUtf8

except AttributeError:
	def _fromUtf8(s):
		return s

username = ""
live_users = ["kanak","abhishek","shaan"]

# kchat = ["Kanak","SDASDAS","dasDASdasdsaSADas"]
# achat = ["Abhi","SDAS","dASdasdsasdasaSADas","a"]
# schat = ["Shaan","ASDAS","dasSADas"]
groups = {"Networks": ["kanak", "abhishek"]}
currentUser = "kanak"
chats = {
	# "kanak":kchat,
	# "abhishek":achat,
	# "shaan":schat,
}

TCP_IP = '10.196.5.108'
TCP_PORT = int(sys.argv[1])
BUFFER_SIZE = 50

SHOW=False

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
	return sent
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
		for user in live_users:
			print "hi"
			exec("item = QCheckBox('"+user+"')")
			self.ui.listWidget_2.addItem(item)


	def logout(self):
		msg = "logout:"
		self.s.send(msg)
		sys.exit(0)

	def sendChat(self):
		global currentUser, groups
		msg = self.ui.textEdit.toPlainText()
		self.ui.textEdit.setPlainText("")
		if(msg!=""):
			if(sendmessage(currentUser,msg,self.s)==0):
				warningbox = QApplication(sys.argv)       
				# The QWidget widget is the base class of all user interface objects in PyQt4.
				windowforwarning = QWidget()
				# Show a message box
				result = QMessageBox.warning(windowforwarning, 'Message', "Message could not be sent. User is offline. Try again later")
				# Show window
				windowforwarning.show() 
				
				sys.exit(warningbox.exec_())
			else:
				if currentUser not in chats:
					x = ["You: "+msg]
					chats[currentUser] = x
				else:
					chats[currentUser].append("You: "+msg)
		
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

		global currentUser
		currentUser = user
		self.ui.listWidget_2.clear()
		# for i in reversed(range(self.ui.verticalLayout_2.count())):
		# self.ui.verticalLayout_2.itemAt(i).widget().deleteLater()
		if user in chats.keys():
			for chat in chats[user]:
				item = QListWidgetItem(chat)
				self.ui.listWidget_2.addItem(item)

	def updateUi(self):

		for i in reversed(range(self.ui.verticalLayout_2.count())):
			self.ui.verticalLayout_2.itemAt(i).widget().deleteLater()

		global live_users, groups
		print live_users
		for user in live_users:
			exec("self.ui.button_"+user+" = QPushButton(self.ui.verticalLayoutWidget_2)")
			exec("self.ui.button_"+user+".setObjectName(_fromUtf8('button_"+user+"'))")
			exec("self.ui.verticalLayout_2.addWidget(self.ui.button_"+user+")")
			exec("self.ui.button_"+user+".setText(user)")
		self.showcurrentchat(currentUser)
		# self.ui.button_Kanak.clicked.connect(lambda : self.showcurrentchat("Kanak"))
		for user in live_users:
			exec("self.ui.button_"+user+".clicked.connect(partial(self.showcurrentchat,user))")
		
		for group in groups.keys():
			exec("self.ui.button_"+group+" = QPushButton(self.ui.verticalLayoutWidget_2)")
			exec("self.ui.button_"+group+".setObjectName(_fromUtf8('button_"+group+"'))")
			exec("self.ui.verticalLayout_2.addWidget(self.ui.button_"+group+")")
			exec("self.ui.button_"+group+".setText(group)")
		self.showcurrentchat(currentUser)
		# self.ui.button_Kanak.clicked.connect(lambda : self.showcurrentchat("Kanak"))
		for group in groups.keys():
			exec("self.ui.button_"+group+".clicked.connect(partial(self.showcurrentchat,group))")	

		# exec("self.connect(self.ui.button_"+user+", SIGNAL('clicked()'), self.showcurrentchat)")


		# self.ui.p2 = QPushButton(self.ui.verticalLayoutWidget_2)
		# self.ui.p2.setObjectName(_fromUtf8("p2"))
		# self.ui.verticalLayout_2.addWidget(self.ui.p2)
		# self.ui.p2.setText("Kanak2")

################################################################################

def func(oper):
	global send,check,live_users,SHOW,username
	# print oper
	while(True):
		if(oper == "send" and send):
			# print oper
			x = raw_input()
			s.send(x)
			send = False
		elif(oper=="recv"):
			data = s.recv(BUFFER_SIZE)
			print data
			temp = data[:data.find(":")]
			if(temp=="msg"):
				data = data[data.find(":")+1:]
				fromwhom = data[:data.find(":")]
				message = data[data.find(":")+1:]
				message = fromwhom+": "+message
				if fromwhom not in chats:
					x = [message]
					chats[fromwhom] = x
				else:
					chats[fromwhom].append(message)
				SHOW = True
			elif(temp=="list"):
				data = data[data.find(":")+1:]
				live_users = data.split(":")
				live_users.remove(username)
				SHOW = True
			elif(temp=='group'):
				data = data[data.find(":")+1:]
				fromwhichgroup = data[:data.find(":")]
				data = data[data.find(":")+1:]
				fromwhom = data[:data.find(":")]
				message = data[data.find(":")+1:]
				message = fromwhom+": "+message
				if fromwhichgroup not in chats:
					x = [message]
					chats[fromwhichgroup] = x
				else:
					chats[fromwhichgroup].append(message)
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
