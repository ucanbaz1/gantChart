"""
Stage Task Reader
Created by Ersin YAYLA
Reads a csv file and update/create a stage config file accordingly
Updates:
- Added an upgrade stage
- Dublicate lines are excluded 
"""
from contextlib import nullcontext
import ctypes
import os.path
import pandas as pd

LogFileNameList = []
StageNameList = []
StageTaskStartList = []
StageTaskEndList = []
CallingStartTask=[]
CallingLogFileName=[]
CallingEndList=[]
CallingStage=[]


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# to collect all file names in the directory 
def logList(path):
    fileNames = []
    with os.scandir(path) as entries:
        for f in entries:
            if f.is_file():
                print(f.name)
                fileNames.append(f.name)
    print(fileNames)
    return fileNames
def getMCPVersion(filename):
    MCP=""
    with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                if "vsphere_file.upload" in line and "MCP" in line and "Creating..." in line:
                    MCP = (line.split('upload')[1]).split(":")[0]
                    print(MCP)
    return MCP
# We are picking up the all NE names in here  
def nameBasedLogTaskReader(filename, Taskname, logname, stageName):
    serverNEList = []
    Taskname = Taskname.strip("<ServerName>")
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                
                # if "MCP Core Upload" in stageName:
                if "vsphere_file.upload" in line and "MCP" in line and "Creating..." in line:
                    ServerNEName = (line.split("Creating...")[1]).split("'")[0]
                elif "vsphere_file.upload" in line and "MCP" in line and "Creation" in line:
                    ServerNEName = (line.split("Creation complete")[1]).split(" after")[0]
                
                elif "VM Creation" in stageName and Taskname in line :
                    ServerNEName = (line.split("disk")[1]).split(".")[0]
                
                # elif ("Config Drive" in stageName or "Create cloud-init ISO" in stageName)  and Taskname in line :
                #     ServerNEName = (line.split(".yml ")[1]).split("\n")[0]
                
                    
                else:
                    if Taskname in line:
                        # if 
                        if "stack" in logname:
                            line = line.split('] ')[1]
                        else:
                            line = line.split('] ')[0]
                        ServerNEName = line.split(":")[1]
                        ServerNEName=(ServerNEName.split(" ")[1]).split(" ")[0]
                        
                        if "\n" in ServerNEName:
                            ServerNEName = ServerNEName.strip("\n")
                        print(ServerNEName)
                        serverNEList.append(ServerNEName)

                    else:
                        continue
                serverNEList.append(ServerNEName)
            f.close()
    except:
        nullcontext
    return serverNEList

# Keeping all data into the lists to write into a Config.csv file
def newConfigFileWriter(stageName, logFileName, startTask, endTask):
    isThere=False
    for i in StageNameList: # Check if stageName is a dublicated data or not 
        if stageName ==i:
            print("{} ---->>>> is already there so skipping".format(i))
            isThere=True
            break
    if not isThere:  #Put into the lists if it is not dublicated  

        LogFileNameList.append(logFileName.split('/')[-1])
        StageNameList.append(stageName)
        StageTaskStartList.append(startTask)
        StageTaskEndList.append(endTask)

    # with open(newFile, 'a') as file:
    #     file.write(stageName+";"+logFileName.split('\\')[-1]+";"+startTask+";"+endTask+"\n")
    #     file.close()

# Creating Config.csv file
def createCSV(logPath):
    newFile = logPath + r'Config.csv'
    data = {'StageName': StageNameList, 'LogFileName': LogFileNameList, 'StageTaskStart': StageTaskStartList,
            'StageTaskEnd': StageTaskEndList}
    df = pd.DataFrame(data)
    df.to_csv(newFile)

# reads the my config file and process based on Stage names 
def ConfigReader(filename, logPath):
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:

            if line.startswith("#") or line.startswith("\n"):
                pass
            else:
                line = line.strip('\n')
                stageName = str(line.split(';')[0]).strip()
                logFileName = logPath + str(line.split(';')[1]).strip()
                startTask = str(line.split(';')[2]).strip()
                endTask = str(line.split(';')[3]).strip()
                if "VM Remove" in stageName and not stageName.startswith("All")  or (stageName=="VM Disk Replacement") or (stageName=="Config Drive") or (stageName=="Create cloud-init ISO"):
                    serverNeList= nameBasedLogTaskReader(logFileName, startTask, logFileName,stageName)
                    for i in serverNeList:
                        prevServerName = "<ServerName>"
                        VMStageName = stageName + " " + i
                        VMStartTask = startTask.replace(prevServerName, i)
                        VMEndTask = endTask.replace(prevServerName, i)
                        print(VMStageName)
                        newConfigFileWriter(VMStageName, logFileName, VMStartTask, VMEndTask)
                        # file.write(stageName+" "+str(i)+";"+logFileName+";"+keyTask+" "+str(i)+";"+VMRemoveEnd+"\n")
                elif "VM Creation" in stageName:
                    serverNeList= nameBasedLogTaskReader(logFileName, startTask, logFileName,stageName)
                    for i in serverNeList:
                        prevServerName = "<ServerName>"
                        VMStageName = stageName + " " + i
                        VMStartTask = startTask.replace(prevServerName, i)
                        VMEndTask = endTask.replace(prevServerName, i)
                        print(VMStageName)
                        newConfigFileWriter(VMStageName, logFileName, VMStartTask, VMEndTask)
                        # file.write(stageName+" "+str(i)+";"+logFileName+";"+keyTask+" "+str(i)+";"+VMRemoveEnd+"\n")

                elif stageName=="MCP Core Upload":
                    serverNeList= nameBasedLogTaskReader(logFileName, startTask, logFileName,stageName)
                    MCP=getMCPVersion(logFileName)
                    for i in serverNeList:
                        prevServerName = "<ServerName>"
                        prevMCP="<MCPCore>"
                        VMStageName = stageName + " " + i
                        VMStartTask = startTask.replace(prevServerName, i)
                        VMStartTask = VMStartTask.replace(prevMCP,MCP)
                        VMEndTask = endTask.replace(prevServerName, i)
                        VMEndTask = VMEndTask.replace(prevMCP, MCP)
                        print(VMStageName)
                        newConfigFileWriter(VMStageName, logFileName, VMStartTask, VMEndTask)
                        # file.write(stageName+" "+str(i)+";"+logFileName+";"+keyTask+" "+str(i)+";"+VMRemoveEnd+"\n")
                elif stageName == "VM Create":
                    serverNeList= nameBasedLogTaskReader(logFileName, startTask, logFileName,stageName)
                    for i in serverNeList:
                        prevServerName = "<ServerName>"
                        VMStageName = stageName + " " + i.split(r"/")[-1].strip("config-")
                        VMStartTask = startTask.replace(prevServerName, i)
                        VMEndTask = endTask.replace(prevServerName, i.split(r"/")[-1].strip("config-"))
                        print(VMStageName)
                        newConfigFileWriter(VMStageName, logFileName, VMStartTask, VMEndTask)

                elif ("VM Upgrade" in stageName and not stageName.startswith("All")):
                    serverNeList= nameBasedLogTaskReader(logFileName, startTask, logFileName,stageName)
                    for i in serverNeList:
                        prevServerName = "<ServerName>"
                        VMStageName = stageName + " " + i
                        VMStartTask = startTask.replace(prevServerName, i)
                        VMEndTask = endTask.replace(prevServerName, i)
                        print(VMStageName)
                        newConfigFileWriter(VMStageName, logFileName, VMStartTask, VMEndTask)

                elif stageName == "Commisioning and Configure logs":
                    fileNameList = logList(logPath)
                    for f in fileNameList:
                        if "-commissioning" in f or "-configure" in f:
                            VMStageName = str(f).strip(".log")
                            logFileName = str(f)
                            VMStartTask = startTask
                            VMEndTask = endTask
                            newConfigFileWriter(VMStageName, logFileName, VMStartTask, VMEndTask)
                        else:
                            pass


                elif "Calling" not in startTask:
                    newConfigFileWriter(stageName, logFileName, startTask, endTask)
            file.close()

def readCallingTasksFromMytrial(filename, logPath):
    with open(filename, "r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("#") or line.startswith("\n"):
                pass
            else:
                line = line.strip('\n')
                if "Calling" in line:
                    CallingStage.append(str(line.split(';')[0]).strip())
                    CallingStartTask.append(str(line.split(';')[2]).strip())
                    CallingEndList.append(str(line.split(';')[3]).strip())
                    
                    if logPath + str(line.split(';')[1]).strip() not in CallingLogFileName:
                         CallingLogFileName.append(logPath + str(line.split(';')[1]).strip())
            

    readCallingTasks(CallingLogFileName,CallingStartTask,CallingStage,CallingEndList)
def readCallingTasks(fileName,startTask,CallingStage,CallingEndList): 
    
    j=0
    i=0
    isExist = os.path.exists(fileName[i])
    if isExist:
        while j < len(startTask):
            with open(fileName[i], "r") as file:
                lines = file.readlines()
                for line in lines:
                    startTask[j] = startTask[j].strip("<ServerName>") 
                    if startTask[j] in line:
                        line = "-e"+(line.split("-e")[1]).split("],")[0]+ "]"
                        VMStageName = CallingStage[j]
                        VMStartTask = str(startTask[j])+ line
                        VMEndTask = str(CallingEndList[j])
                        print(VMStageName)
                        newConfigFileWriter(VMStageName, CallingLogFileName[i], VMStartTask, VMEndTask)
                        j += 1
                    if j == len(startTask):
                        break
                i += 1


def getInputPath(fileFullPath):
    logPath = fileFullPath.split("myTrial")[0]
    print(logPath)
    try:
        os.remove(logPath + "Config.csv")
    except OSError:
        pass

    ConfigReader(fileFullPath, logPath)
    readCallingTasksFromMytrial(fileFullPath, logPath)
    createCSV(logPath)

#fileFullPath= input("PLease insert Stage config file starting with \"my\":")
#getInputPath(fileFullPath)