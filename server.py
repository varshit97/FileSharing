# server.py

from subprocess import Popen,PIPE
import socket                   # Import socket module
import commands
import os.path, time, glob
import re
import os

# mypath = os.getcwd()
mypath = ['/home/ramkumar/cn_assi/FileSharing/']
def test(f,start,end):
    if os.path.isfile(f):
        mode,ino,dev,nlink,uid,gid,size,atime,mtime,ctime=os.stat(f)
        return start<=ctime and end>=ctime
    else:
        return 0
def checkfilepath(filename,mypath):
    output = showallfolders(mypath)
    files=[]
    for w in range(len(output)):
        tempfiles = [f for f in glob.glob(os.path.join(output[w], "*"))]
        files+=tempfiles
    for i in range(len(files)):
        if filename in files[i]:
            print files[i]
            return 1
    return 0


def calculateMD5Sum(fileName):
    (status,output)=commands.getstatusoutput('md5sum %s'%(fileName))
    return str(output.split('  ')[0])

def showFiles():
    res=Popen(['ls'],stdout=PIPE)
    return res.stdout.read()

def showDetails():
    res=Popen(['ls','-lR'],stdout=PIPE)
    return res.stdout.read()

def showallfolders(mypath):
    (status,output)=commands.getstatusoutput('find %s -not -path "*/\.*" -type d' %(mypath[0]))
    output=output.split('\n')
    return output

port = 60001                    # Reserve a port for your service.
s = socket.socket()             # Create a socket object
host = socket.gethostname()     # Get local machine name
s.bind(('0.0.0.0', port))            # Bind to the port
s.listen(5)       
empty=''              # Now wait for client connection.

print 'Server listening....'

conn, addr = s.accept()     # Establish connection with client.
fileInfo={}
times=[]
history=[]
while True:
    #print 'Got connection from', addr
    #Data sent from clientside
    data = conn.recv(1024)
    if not data:
        conn, addr = s.accept()     # Establish connection with client.
        continue
    print('Server received', data)
    history.append('data')

    #Files Information

    output = showallfolders(mypath)
    files=[]
    for w in range(len(output)):
        tempfiles = [f for f in glob.glob(os.path.join(output[w], "*"))]
        files+=tempfiles

    files=showFiles()
    allFiles=files.split('\n')
    for i in allFiles:
        if i!='':
            fileInfo[i]=[calculateMD5Sum(i),time.ctime(os.path.getmtime(i))]

    #Handling requests
    if data=='ls':
        fileList=showFiles()
        conn.send(fileList)

    elif data=="shortlist":
        conn.send("ty")
        start = conn.recv(1024)
        conn.send("ty")
        end = conn.recv(1024)
        # find . -type d -name "*" -print
        output = showallfolders(mypath)
        files=[]
        for w in range(len(output)):
            tempfiles = [f for f in glob.glob(os.path.join(output[w], "*")) if test(f,int(start),int(end))]
            files+=tempfiles        
        for i in range(len(files)):
            (status,output)=commands.getstatusoutput('ls -l %s'%(files[i]))
            if(output[0]=='-'):
                output += "   File"
            else:
                output += "   Folder"
            files[i]=output
        for i in range(len(files)):
            conn.send(files[i])
            print conn.recv(1024)
            print('Sent ',files[i])
        conn.send('0')

    elif data=='ls -lR':
        details=showDetails()
        conn.send(details)

    elif 'regex' in data.split(' '):
        matchedFiles=''
        regex=data.split(' ')[2]
        try:
            checkMatch=re.compile(regex)
        except:
            conn.send("Invalid regex")
            continue
        for yy in range(len(files)):
            files[yy] = files[yy].split('/')[-1]
        for i in files:
            matched=checkMatch.findall(i)
            if matched:
                matchedFiles+=i+'\n'
        conn.send(matchedFiles)

    elif 'verify' in data:
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
        if calculateMD5Sum(data.split(' ')[2])==data.split(' ')[1]:
            conn.send('1')
        else:
            conn.send('0')
        # sendTo=fileInfo[data.split(' ')[1]]
        # conn.send(sendTo[0]+sendTo[1])

    elif 'checkall' in data:
        info=fileInfo.values()
        names=fileInfo.keys()
        string=""
        count=0
        for i in info:
            string+=names[count]+' '+str(i)+'\n'
            count+=1
        conn.send(string)

    elif data.split(' ')[0]=='Download':
        validfile=0
        filename=data.split(' ')[1]
        validfile = checkfilepath(filename,mypath)
        if(validfile==0):
            conn.send('Invalid')
            continue
        f = open(filename,'rb')
        l = f.read(1024)
        while(l):
            conn.send(l)
            print conn.recv(1024)
            print('Sent ',repr(l))
            l = f.read(1024)
        conn.send('1983')
        f.close()
        msum = calculateMD5Sum(filename)
        # print msum
        conn.send(msum)
        print('Done sending')

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
conn.close()


