# server.py

from subprocess import Popen,PIPE
import socket                   # Import socket module
import commands

port = 60001                    # Reserve a port for your service.
s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind(('0.0.0.0', port))            # Bind to the port
s.listen(5)                     # Now wait for client connection.

print 'Server listening....'

while True:
    conn, addr = s.accept()     # Establish connection with client.
    print 'Got connection from', addr
    #Data sent from clientside
    data = conn.recv(2048)
    print('Server received', repr(data))
    if data=='ls':
        res=Popen(['ls'],stdout=PIPE)
        conn.send(res.stdout.read())
    filename='mytext.txt'
    (status,output)=commands.getstatusoutput('md5sum mytext.txt')
    conn.send(str(output))
    f = open(filename,'rb')
    l = f.read(1024)
    while (l):
       conn.send(l)
       print('Sent ',repr(l))
       l = f.read(1024)
    f.close()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Done sending')
    # conn.send('Thank you for connecting')
    conn.close()

