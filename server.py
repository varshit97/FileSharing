# server.py

from subprocess import Popen,PIPE
import socket                   # Import socket module
import commands


def calculateMD5Sum(fileName):
    (status,output)=commands.getstatusoutput('md5sum %s'%(fileName))
    return str(output.split('  '))[0]

def showFiles():
    res=Popen(['ls'],stdout=PIPE)
    return res.stdout.read()

port = 60000                    # Reserve a port for your service.
s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind(('0.0.0.0', port))            # Bind to the port
s.listen(5)       
empty=''              # Now wait for client connection.

print 'Server listening....'

conn, addr = s.accept()     # Establish connection with client.

while True:
    #print 'Got connection from', addr
    #Data sent from clientside
    data = conn.recv(1024)
    print('Server received', repr(data))
    if(data=='exit'):
        continue
    if data=='ls':
        fileList=showFiles()
        conn.send(fileList)
    elif data.split(' ')[0]=='Download':
        filename=data.split(' ')[1]
        f = open(filename,'rb')
        l = f.read(1024)
        while(l):
            conn.send(l)
            print('Sent ',repr(l))
            l = f.read(1024)
        conn.send('0')
        f.close()
        print('Done sending')
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # conn.send('Thank you for connecting')
conn.close()

