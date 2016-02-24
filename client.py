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
port = 60001                    # Reserve a port for your service.

requests=[]

s.connect((x, port))



while True:
    #Take input
    command=raw_input("Enter Command : ")
    requests.append(command)

    #Handle requests
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

    elif command=='IndexGet history':
        for i in range(len(requests)):
            print requests[i]
        print

    elif command=='IndexGet longlist':
        s.send("ls -lR")
        details=s.recv(1024)
        print details

    elif 'IndexGet regex' in command:
        s.send(command)
        matchedFiles=s.recv(1024)
        print matchedFiles

    elif 'FileHash' in command:
        if command.split(' ')[1]=='verify':
            s.send('verify '+calculateMD5Sum(command.split(' ')[2])+' '+command.split(' ')[2])
        elif command.split(' ')[1]=='checkall':
            s.send('checkall')
        res=int(s.recv(1024))
        if(res==1):
            print "You are up-to-date"
        else:
            print "You are not up-to-date"

    elif command=='exit':
        s.send('exit')
        break

    elif command.split(' ')[0]=='Download':
        # filename = "fromserver.txt"   
        filename = command.split(' ')[1]
        s.send(command)
        with open(filename, 'wb') as f:
            print 'file opened'
            while True:
                print('receiving data...')
                data = s.recv(1024)
                if data=='Invalid':
                    print "Invaid File given"
                    break
                s.send('new')
                print('data=%s', (data))
                if(data=='1983'):
                    break
                # write data to a file
                f.write(data)
        f.close()
        if(data=='Invalid'):
            continue
        md5=calculateMD5Sum(filename)
        servermd5=s.recv(1024)
        if servermd5==md5:
            print "File downloaded successfully"
        else:
            print "File download not successful.Retry :("

    else:
        print "Not a correct command try again"

s.close()
print('connection closed')