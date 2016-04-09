
#!/usr/bin/python

import signal
import sys
import socket
import SocketServer
from threading import Thread
import commands

def signal_handler(signal, frame):
    sys.exit(0)

def verify(filename):
    md5sum = commands.getoutput("md5sum " + filename)
    glm = commands.getoutput("stat " + filename)
    glm = glm.split()
    timestamp = ""
    for i in range(0, len(glm)):
        if glm[i] == "Modify:":
            timestamp += glm[i+1] + " " + glm[i+2]

    return md5sum + " " + timestamp


class Server(Thread) :
    def __init__(self, host, port):
        Thread.__init__(self)
        self.port = port
        self.host = host
        self.bufsize = 1024
        self.addr = (host, port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.addr)

    def run(self):
        self.socket.listen(5)
        while True:
            print "waiting for connection"
            client, caddr = self.socket.accept()
            print "connected to ", caddr
            
            while True:
                data = client.recv(self.bufsize)
                if not data:
                    break
                elif data == "close":
                    self.socket.close()
                    sys.exit(0)
                    print "\nhello\n"

                data = data.split()

                if data[0] == "IndexGet" :
                    print "indexGet command called \n"

                    if data[1] == "shortlist":
                        response = commands.getoutput("find . -newermt "+ data[2] +"! -newermt " + data[3] -ls)
                        client.sendall(response + "\n\n")

                    elif data[1] == "longlist":
                        response = commands.getoutput("find . -ls")
                        client.sendall(response + "\n\n")
                        
                    elif data[1] == "regex":
                        response = commands.getoutput("find . -iregex '\./"+ data[2] + "' -ls")
                        client.sendall(response + "\n\n")
                        
                    else:
                     #   print "wrong command \n"
                        client.sendall("wrong command \n")
                
                if data[0] == 'FileHash':
                    if data[1] == 'verify':
                        response = verify(data[2])
                        client.sendall(response)
                                
                    elif data[1] == 'checkall':
                        fileList = commands.getoutput('ls')
                        fileList = fileList.split('\n')
                        response = ""
                        for i in fileList:
                            response += verify(i) + "\n"
                        client.sendall(response)

                    else:
                        client.sendall("command not found\n\n")
                
                if data[0] == "FileDownload":
                    if data[1] == 'TCP':
                        checksumTimestamp = verify(data[2])
                        size = commands.getoutput("stat " + data[2])
                        size = size.split()
                        size = size[3]
                        response1 = checksumTimestamp + "  " + size
                        client.sendall(response1)
                        self.size = response1.split()[-1]
                        f = open(data[2], 'rb')
                        l = f.read(1024)
                        while(l):
                            client.send(l)
                            l = f.read(1024)
                        f.close()
                        print "file sent via TCP"

                    elif data[1] == 'UDP':
                        self.udpServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.server_address = ("localhost", 1234)
                        self.udpServer.bind(self.server_address)
                        self.udpdata, self.udpaddress = self.udpServer.recvfrom(1024)
                      #  send = self.udpServer.sendto(response1, self.udpaddress)
                        if self.udpdata:
                            print "data recieved from client"
                            f= open(data[2], 'rb')
                            l = f.read(1024)
                            while True:
                                send = self.udpServer.sendto(l, self.udpaddress)
                                l = f.read(1024)
                            self.udpServer.close()
                            print "File sent via udp"
                        
                      
                    else:
                        client.sendall("command not found")

                else:        
                    #print data
                    client.sendall("OK\n")



class Client(Thread) :
    def __init__(self, host, port) :
        Thread.__init__(self)
        self.port = port
        self.host = host
        self.bufsize = 1024
        self.addr = (host, port)
        self.buf = 1024

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def run(self):
        invalid = True
        while invalid :
            try :
                invalid = False
                self.socket.connect(self.addr)
            except:
                invalid = True

        while True:
            data = raw_input(' Enter Your command -> ')
            if not data :
                continue
            self.socket.send(data)
            response = self.socket.recv(self.bufsize)
            print response
            data = data.split()
            if data[0] == "FileDownload" and data[1] == "TCP":
                response = response.split()
                size = int(response[-1])
                chunkSize = 0
                with open('received_file', 'wb') as f:
                    while chunkSize < size:
                        temp = self.socket.recv(1024)
                        if not temp:
                            break
                        f.write(temp)
                        chunkSize += 1024
                f.close()
                print "File Downloaded via TCP"

            if data[0] == "FileDownload" and data[1] == "UDP":
                self.udpClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.server_address = ("localhost", 1234)
                sent = self.udpClient.sendto("hello", self.server_address)
                f = open('received_file_udp', 'wb')
                temp,server = self.udpClient.recvfrom(1024)
                while temp:
                    print "started receiving"
                    f.write(temp)
                    temp, server = self.udpClient.recvfrom(1024)
                self.udpClient.close()
                f.close()
                print "File received via UDP"
              


if __name__ == '__main__':
    try:
        host = ''
        p1 = input("enter port for server  ")
        p2 = input("enter port for client  ")
    
       # signal.signal(signal.SIGINT, signal_handler)
        server = Server(host, p2)
        client = Client(host, p1)

        server.start()
        client.start()

        server.join()

    except KeyboardInterrupt:
        server.socket.close()
        sys.exit(0)



