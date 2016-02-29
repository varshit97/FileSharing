# server.py

#Imports
from subprocess import Popen,PIPE
import socket                   # Import socket module
import commands
import os.path, time, glob
import re
import os,magic

mypath = os.getcwd()

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
    (status,res)=commands.getstatusoutput('ls -lR')
    # res=Popen(['ls','-lR'],stdout=PIPE)
    res=res.split('\n')
    output=''
    foldername=''
    for i in range(len(res)):
        if res[i]=='':
            continue
        if res[i][0]=='.':
            foldername = res[i].split(':')[0][2:]
        if(res[i][0]=='-' or res[i][0]=='d'):
            if(foldername!=''):
                filen = foldername+"/"+res[i].split(' ')[-1]
            else:
                filen = res[i].split(' ')[-1]
            (status,times)=commands.getstatusoutput('stat %s | cut -d. -f1'%(filen))
            (status,filetype)=commands.getstatusoutput('file --mime-type -b %s'%(filen))
            times=times.split('\n')[5]
            size = os.path.getsize(filen)
            output+=filen+" "+str(size)+" "+times.split(':')[1]+" "+filetype+'\n' 
        else:
            output+=res[i]+'\n'

    return output

def showallfolders(mypath):
    (status,output)=commands.getstatusoutput('find %s -not -path "*/\.*" -type d' %(mypath))
    output=output.split('\n')
    return output

port = 60001                                                # Reserve a port for your service.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       # Create a socket object
host = socket.gethostname()                                 # Get local machine name
s.bind(('0.0.0.0', port))                                   # Bind to the port
s.listen(5)       
u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        # Create a socket object
u.bind(('0.0.0.0',60002))                                   # Bind to the port

print 'Server listening....'

addr2 = None

#Identify if user asked for TCP or UDP
conn, addr1 = s.accept()                                     # Establish connection with client.
temp=conn.recv(1024)
if temp=='1':
    protocol='1'
if temp=='2':
    protocol='2'

def sendInfo(tcporudp,data):
    if tcporudp=='1':
        print data
        conn.send(data)
    elif tcporudp=='2':
        u.sendto(data,addr2)

def recvInfo(tcporudp,data):
    if tcporudp=='1':
        getData=conn.recv(data)
    elif tcporudp=='2':
        getData=u.recvfrom(data)
    return getData

fileInfo={}
times=[]
history=[]

output = showallfolders(mypath)
files=[]
for w in range(len(output)):
    tempfiles = [f for f in glob.glob(os.path.join(output[w], "*"))]
    files+=tempfiles
print files

while True:
    #Data sent from clientside
    if protocol=='1':
        data = recvInfo(protocol,1024)
    if protocol=='2':
        data,addr = recvInfo(protocol,1024)
        addr2 = addr
    if not data:
        if protocol=='1':
            conn, addr = s.accept()                             # Establish connection with client.
        if protocol=='2':
            data = recvInfo(protocol,1024)
        continue

    print('Server received', data)
    history.append('data')

    #Files Information
    

    # files=showFiles()
    # allFiles=files.split('\n')
    allFiles=files
    for i in allFiles:
        if i!='':
            fileInfo[i]=[calculateMD5Sum(i),time.ctime(os.path.getmtime(i))]

    #Handling requests
    if data=='ls':
        fileList=showFiles()
        sendInfo(protocol,fileList)

    elif data=="shortlist":
        sendInfo(protocol,"ty")
        start = recvInfo(protocol,1024)
        sendInfo(protocol,"ty")
        end = recvInfo(protocol,1024)

        # find . -type d -name "*" -print
        output = showallfolders(mypath)
        shortfiles=[]
        for w in range(len(output)):
            tempfiles = [f for f in glob.glob(os.path.join(output[w], "*")) if test(f,int(start),int(end))]
            shortfiles+=tempfiles        
        for i in range(len(tempfiles)):
            (status,output)=commands.getstatusoutput('ls -l %s'%(tempfiles[i]))
            if(output[0]=='-'):
                output += "   File"
            else:
                output += "   Folder"
            tempfiles[i]=output
        for i in range(len(tempfiles)):
            sendInfo(protocol,tempfiles[i])
            print recvInfo(protocol,1024)
            print('Sent ',files[i])
        sendInfo(protocol,'0')

    elif data=='ls -lR':
        details=showDetails()
        sendInfo(protocol,details)

    elif 'regex' in data.split(' '):
        matchedFiles=''
        regex=data.split(' ')[2]
        try:
            checkMatch=re.compile(regex)
        except:
            sendInfo(protocol,"Invalid regex")
            continue
        tempfiles=[]
        for yy in range(len(files)):
            tempfiles.append(files[yy].split('/')[-1])
        for i in tempfiles:
            matched=checkMatch.findall(i)
            if matched:
                matchedFiles+=i+'\n'
        sendInfo(protocol,matchedFiles)

    elif 'verify' in data:
        if calculateMD5Sum(data.split(' ')[2])==data.split(' ')[1]:
            sendInfo(protocol,'1')
        else:
            sendInfo(protocol,'0')
        #sendTo=fileInfo[data.split(' ')[1]]
        #sendInfo(sendTo[0]+sendTo[1])

    elif 'checkall' in data:
        info=fileInfo.values()
        names=fileInfo.keys()
        string=""
        count=0
        for i in info:
            string+=names[count]+' '+str(i)+'\n'
            count+=1
        sendInfo(protocol,string)

    elif data.split(' ')[0]=='Download':
        validfile=0
        filename=data.split(' ')[1]
        validfile = checkfilepath(filename,mypath)
        if(validfile==0):
            sendInfo(protocol,'Invalid')
            continue
        f = open(filename,'rb')
        l = f.read(1024)
        while(l):
            sendInfo(protocol,l)
            print recvInfo(protocol,1024)
            print('Sent ',repr(l))
            l = f.read(1024)
        sendInfo(protocol,'1983')
        f.close()
        msum = calculateMD5Sum(filename)
        sendInfo(protocol,msum)
        print('Done sending')

s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
conn.close()
