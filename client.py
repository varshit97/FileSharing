# client.py

import socket                   # Import socket module
import commands,calendar
from datetime import datetime
import re,glob

def calculateMD5Sum(fileName):
    (status,output)=commands.getstatusoutput('md5sum %s'%(fileName))
    return str(output.split('  ')[0])


(status,output)=commands.getstatusoutput('ifconfig')
output=str(output)
x = re.search(r'inet addr:(\S+)',output)
x=str(x.groups(1))[2:-3]

s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
port = 60002                    # Reserve a port for your service.

requests=[]

s.connect((x, port))

while True:
    command=raw_input("Enter Command : ")
    requests.append(command)
    if 'IndexGet shortlist' in command:
        command = command.split(" ")
        start = command[2]+" "+command[3]
        end = command[4]+" "+command[5]
        timefmt = "%Y%m%d %H:%M:%S"
        start = calendar.timegm(datetime.strptime(start, timefmt).timetuple())
        end = calendar.timegm(datetime.strptime(end, timefmt).timetuple())
        s.send("shortlist")
        s.recv(1024)
        s.send(str(start))
        s.recv(1024)
        s.send(str(end))
        while True:
                data = s.recv(1024)
                s.send('new')
                if(data=='0'):
                    break
                print(data)
        print
    if command=='IndexGet longlist':
        s.send("ls -l")
        details=s.recv(1024)
        print details
    if 'FileHash' in command:
        if command.split(' ')[1]=='verify':
            s.send('verify '+command.split(' ')[2])
        elif command.split(' ')[1]=='checkall':
            s.send('checkall')
        res=s.recv(1024)
        print res
    if command=='exit':
    	s.send('exit')
        break
    elif command=='Download mytext.txt':
        filename='fromserver.txt'
        s.send("Download mytext.txt")
        #checkvalue = s.recv(1024)
        #filename = checkvalue.split('  ')[1]+'1'
        #checkvalue = checkvalue.split('  ')[0]
        with open(filename, 'wb') as f:
            print 'file opened'
            while True:
                print('receiving data...')
                data = s.recv(1024)
                s.send('new')
                print('data=%s', (data))
                if(data=='0'):
                    break
                # write data to a file
                f.write(data)
        f.close()
        md5=calculateMD5Sum(filename)
        servermd5=s.recv(1024)
        if servermd5==md5:
            print "Thope ayyav ga"
        else:
            print "pulka raja"
#        (status,output)=commands.getstatusoutput('md5sum %s' %(filename))
#        if(checkvalue==output.split('  ')[0]):
#	    print 'File Transfered properly'
# print output.split('  ')[0]
#print('Successfully get the file')
s.close()
print('connection closed')
