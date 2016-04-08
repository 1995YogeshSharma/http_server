#!/usr/bin/python

import socket
import commands 
import os
import sys


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
			startLine = request.split('\n')[0]
			method, path, version = startLine.split()
			curDir = commands.getoutput('pwd')
			fileRequested = curDir + path
			print fileRequested
			if not os.path.exists(fileRequested) :
				print "file not found on the server"
				client.sendall('''HTTP/1.1 404 Not Found
					Date: Sun, 18 Oct 2012 10:36:20 GMT
					Server: Apache/2.2.14 (Win32)
					Content-Length: 230
					Connection: Closed
					Content-Type: text/html; charset=iso-8859-1''')
			else:
				with open(fileRequested) as f :
					data = f.read()
					response = RESPONSE.format(data)
					client.sendall(response)
			client.close();




