# server.py

from subprocess import Popen,PIPE
import socket                   # Import socket module
import commands
import os.path, time
import re
import os.path, time, glob

mypath = "/home/ramkumar/cn_assi/FileSharing"

def test(f,start,end):
    if (not os.path.isfile(f)):
        return 0
    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(f)
    return start<=ctime and end>=ctime

def calculateMD5Sum(fileName):
    (status,output)=commands.getstatusoutput('md5sum %s'%(fileName))
    return str(output.split('  ')[0])

def showFiles():
    res=Popen(['ls'],stdout=PIPE)
    return res.stdout.read()

def showDetails():
    res=Popen(['ls','-l'],stdout=PIPE)
    return res.stdout.read()

port = 60002                    # Reserve a port for your service.
s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind(('0.0.0.0', port))            # Bind to the port
s.listen(5)       
empty=''              # Now wait for client connection.

print 'Server listening....'

conn, addr = s.accept()     # Establish connection with client.
fileInfo={}
times=[]

while True:
    #print 'Got connection from', addr
    #Data sent from clientside
    data = conn.recv(1024)
    if not data:
        conn, addr = s.accept()     # Establish connection with client.
        #print "In if '%s' " %data
        continue
    print('Server received', data)
    files=showFiles()
    allFiles=files.split('\n')
    for i in allFiles:
        if i!='':
            fileInfo[i]=[calculateMD5Sum(i),time.ctime(os.path.getmtime(i))]
    if data=='ls':
        fileList=showFiles()
        conn.send(fileList)
    if data=="shortlist":
        conn.send("ty")
        start = conn.recv(1024)
        conn.send("ty")
        end = conn.recv(1024)
        files = [f for f in glob.glob(os.path.join(mypath, "*")) if test(f,int(start),int(end))]
        print files
        for i in range(len(files)):
            conn.send(files[i])
            print conn.recv(1024)
            print('Sent ',files[i])
        conn.send('0')
        print start," ",end
    if data=='ls -l':
        details=showDetails()
        conn.send(details)
    if 'regex' in data:
        matchedFiles=''
        regex=data.split(' ')[2]
        checkMatch=re.compile(regex)
        for i in allFiles:
            matched=checkMatch.findall(i)
            if matched:
                matchedFiles+=i+'\n'
        conn.send(matchedFiles)
    if 'verify' in data:
        """f=open('details','r')
        total=f.readlines()
        f.close()
        filesCount=len(files.split('\n'))-1
        if total[0]<filesCount:
            detailFile=open('details','w')
            detailFile.truncate()
            detailFile.write(filesCount)
            detailFile.write('vish pandu\n')
            detailFile.close()"""
        sendTo=fileInfo[data.split(' ')[1]]
        conn.send(sendTo[0]+sendTo[1])
    if 'checkall' in data:
        info=fileInfo.values()
        names=fileInfo.keys()
        string=""
        count=0
        for i in info:
            string+=names[count]+' '+str(i)+'\n'
            count+=1
        conn.send(string)
    elif data.split(' ')[0]=='Download':
        filename=data.split(' ')[1]
        f = open(filename,'rb')
        l = f.read(1024)
        while(l):
            conn.send(l)
            # conn.close()
            # conn, addr = s.accept()
            print conn.recv(1024)
            print('Sent ',repr(l))
            l = f.read(1024)
        conn.send('0')
        f.close()
        msum = calculateMD5Sum(filename)
        # print msum
        conn.send(msum)
        print('Done sending')
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # conn.send('Thank you for connecting')
conn.close()


