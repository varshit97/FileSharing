# client.py

#Imports
import socket                                                   # Import socket module
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

port = 60001                                                    # Reserve a port for your service.

requests=[]

serverIp=raw_input("Enter IP of server: ")
protocol=raw_input("Press 1 for TCP and 2 for UDP: ")

if protocol=='1':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a socket object
    host = socket.gethostname()                                 # Get local machine name
    s.connect((serverIp, port))
    s.send('1')
else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a socket object
    s.connect((serverIp, port))
    s.send('2')
    s.close()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        # Create a socket object
    s.connect((serverIp, 60002))

def sendInfo(tcporudp,data):
    if tcporudp=='1':
        s.send(data)
    elif tcporudp=='2':
        s.sendto(data,('10.1.39.145',60002))

def recvInfo(tcporudp,data):
    if tcporudp=='1':
        getData=s.recv(data)
    elif tcporudp=='2':
        getData,addr=s.recvfrom(data)
    return getData

while True:
    #Take input
    command=raw_input("Enter Command : ")
    
    #Storing requests
    requests.append(command)

    #Handle requests
    if 'IndexGet shortlist' in command:
        command = command.split(" ")
        start = command[2]+" "+command[3]
        end = command[4]+" "+command[5]
        timefmt = "%Y%m%d %H:%M:%S"
        start = calendar.timegm(datetime.strptime(start, timefmt).timetuple())
        end = calendar.timegm(datetime.strptime(end, timefmt).timetuple())
        sendInfo(protocol,'shortlist')
        recvInfo(protocol,1024)
        sendInfo(protocol,str(start))
        recvInfo(protocol,1024)
        sendInfo(protocol,str(end))
        while True:
                data = recvInfo(protocol,1024)
                sendInfo(protocol,'new')
                if(data=='0'):
                    break
                print(data)
        print

    elif command=='IndexGet history':
        for i in range(len(requests)):
            print requests[i]
        print

    elif command=='IndexGet longlist':
        sendInfo(protocol,'ls -lR')
        details=recvInfo(protocol,1024)
        print details

    elif 'IndexGet regex' in command:
        sendInfo(protocol,command)
        matchedFiles=recvInfo(protocol,1024)
        print matchedFiles

    elif 'FileHash' in command:
        if command.split(' ')[1]=='verify':
            sendInfo(protocol,'verify '+calculateMD5Sum(command.split(' ')[2])+' '+command.split(' ')[2])
            res=int(recvInfo(protocol,1024))
            if(res==1):
                print "You are up-to-date"
            else:
                print "You are not up-to-date"
        elif command.split(' ')[1]=='checkall':
            sendInfo(protocol,'checkall')
            res=recvInfo(protocol,1024)
            print res

    elif command=='exit':
        sendInfo(protocol,'exit')
        break

    elif command.split(' ')[0]=='Download':
        filename = command.split(' ')[1]
        sendInfo(protocol,command)
        with open(filename, 'wb') as f:
            print 'file opened'
            while True:
                print('receiving data...')
                data = recvInfo(protocol,1024)
                if data=='Invalid':
                    print "Invaid File given"
                    break
                sendInfo(protocol,'new')
                print('data=%s', (data))
                if(data=='1'+'9'+'8'+'3'):
                    break
                f.write(data)
        f.close()
        if(data=='Invalid'):
            continue
        md5=calculateMD5Sum(filename)
        servermd5=recvInfo(protocol,1024)
        if servermd5==md5:
            print "File downloaded successfully"
        else:
            print "File download not successful.Retry :("

    else:
        print "Not a correct command try again"

s.close()
print('connection closed')
