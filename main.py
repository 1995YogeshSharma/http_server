#!/usr/bin/python

import server

if __name__ == '__main__' :
	host = ""
	p = input("enter port number for the server ->  ")
	serv = server.Server(host, p)
	serv.start()