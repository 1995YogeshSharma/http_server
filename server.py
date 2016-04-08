#!/usr/bin/python

import socket 

class Server() :
	def __init__(self, host, port) :
		#defining a socket
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try :
			self.socket.bind((host,port))
			print "port binding done"
		except:
			print "Error: unable to bind socket to given port"

		#declaring other variables
		self.bufsize = 2048

	def start(self) :
		self.socket.listen(1)
		while True:
			print "waiting for connection"
			client, caddr = self.socket.accept()
			print "connected to ", caddr
			data = client.recv(self.bufsize)
			print data.split()
