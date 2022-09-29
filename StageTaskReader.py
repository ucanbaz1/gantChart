"""
Stage Task Reader
Created by Ersin YAYLA
Reads a csv file and update/create a stage config file accordingly 
"""
import ctypes
import os.path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def logList(path):
    fileNames=[]
    with os.scandir(path) as entries:
        for f in entries:
            if f.is_file():
                print(f.name)
                fileNames.append(f.name)
    print(fileNames)
    return fileNames

def nameBasedLogTaskReader(filename,Taskname,logname):
    serverNEList = []
    Taskname = Taskname.strip("<ServerName>")
    with open(filename,"r") as f:
        lines = f.readlines()

        for line in lines:
            if Taskname in line:
                if "stackAPI" in logname:
                    line = line.split('] ')[1]
                else:
                    line=line.split('] ')[0]
                ServerNEName = line.split(" ")[-1]
                print(ServerNEName)
                serverNEList.append(ServerNEName)

            else:
                continue
        f.close()

    return serverNEList

def newConfigFileWriter(stageName,logFileName,startTask,endTask,logPath):
    newFile=logPath+"Config.csv"
    with open(newFile, 'a') as file:
        file.write(stageName+";"+logFileName.split('\\')[-1]+";"+startTask+";"+endTask+"\n")
        file.close()

def ConfigReader(filename,logPath):
    with open(filename,"r") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("#") or line.startswith("\n"):
                pass
            else:
                line=line.strip('\n')
                stageName = str(line.split(';')[0]).strip()
                logFileName = logPath+str(line.split(';')[1]).strip()
                startTask = str(line.split(';')[2]).strip()
                endTask=str(line.split(';')[3]).strip()
                if "VM Remove" in stageName and not stageName.startswith("All"):
                    serverNeList=nameBasedLogTaskReader(logFileName, startTask,logFileName)
                    for i in serverNeList:
                        prevServerName = "<ServerName>"
                        VMStageName = stageName + " " + i
                        VMStartTask = startTask.replace(prevServerName, i)
                        VMEndTask = endTask.replace(prevServerName,i)
                        print(VMStageName)
                        newConfigFileWriter(VMStageName,logFileName,VMStartTask,VMEndTask,logPath)
                            #file.write(stageName+" "+str(i)+";"+logFileName+";"+keyTask+" "+str(i)+";"+VMRemoveEnd+"\n")

                elif stageName=="VM Create":
                    serverNeList = nameBasedLogTaskReader(logFileName, startTask,logFileName)
                    for i in serverNeList:
                        prevServerName = "<ServerName>"
                        VMStageName = stageName + " " + i.split(r"/")[-1].strip("config-")
                        VMStartTask = startTask.replace(prevServerName, i)
                        VMEndTask = endTask.replace(prevServerName, i.split(r"/")[-1].strip("config-"))
                        print(VMStageName)
                        newConfigFileWriter(VMStageName, logFileName, VMStartTask, VMEndTask,logPath)
                elif stageName=="Commisioning and Configure logs":
                    fileNameList=logList(logPath)
                    for f in fileNameList:
                        if "-commissioning" in f or "-configure" in f:
                            VMStageName = str(f).strip(".log")
                            logFileName = str(f)
                            VMStartTask = startTask
                            VMEndTask = endTask
                            newConfigFileWriter(VMStageName, logFileName, VMStartTask, VMEndTask,logPath)
                        else:
                            pass


                else:
                    newConfigFileWriter(stageName,logFileName,startTask,endTask,logPath)
            file.close()



fileFullPath = input("Please provide the config file with full path: ")
logPath=fileFullPath.strip(fileFullPath.split("\\")[-1])
print(logPath)
try:
    os.remove("Config.csv")
except OSError:
    pass

ConfigReader(fileFullPath,logPath)
