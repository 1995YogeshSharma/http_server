#!/usr/bin/python

import socket
import commands 
import os
import sys
import thread


RESPONSE = """HTTP/1.1 200 OK

{}"""

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
			request = client.recv(self.bufsize)
			print "received request header"
			print request
			thread.start_new_thread(do_work, (client, request,))
			
def do_work(client, request):
	startLine = request.split('\n')[0]
	method, path, version = startLine.split()
	curDir = commands.getoutput('pwd')
	fileRequested = curDir + path
	print fileRequested
	if not os.path.exists(fileRequested) :
		print "file not found on the server"
		client.sendall('HTTP/1.1 404 Not Found ')
	else:
		with open(fileRequested) as f :
			data = f.read()
			response = RESPONSE.format(data)
			client.sendall(response)
	client.close()




