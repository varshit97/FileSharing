# client.py

import socket                   # Import socket module
import commands
import re

(status,output)=commands.getstatusoutput('ifconfig')
output=str(output)
x = re.search(r'inet addr:(\S+)',output)
x=str(x.groups(1))[2:-3]

s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
port = 60001                    # Reserve a port for your service.

s.connect((x, port))

while True:
    command=raw_input("Enter Command : ")
    if command=='ls':
        s.send("ls")
        lsoutput = s.recv(1024) 
        print lsoutput
    if command=='exit':
        break
    else:
        filename='mytext.txt'
        #checkvalue = s.recv(1024)
        #filename = checkvalue.split('  ')[1]+'1'
        #checkvalue = checkvalue.split('  ')[0]
        with open(filename, 'wb') as f:
            print 'file opened'
            while True:
                print('receiving data...')
                data = s.recv(1024)
                print('data=%s', (data))
                if not data:
                    break
                # write data to a file
                f.write(data)
        f.close()
#        (status,output)=commands.getstatusoutput('md5sum %s' %(filename))
#        if(checkvalue==output.split('  ')[0]):
#	    print 'File Transfered properly'
# print output.split('  ')[0]
#print('Successfully get the file')
s.close()
print('connection closed')
