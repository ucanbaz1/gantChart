from contextlib import nullcontext
from lib2to3.pgen2.token import NAME
from datetime import datetime
import os
# from RAF_Log_Reader import readFirstTime
from figureCreator import  figCreate
import pandas as pd
import csv
from collections import defaultdict
from figureCreator import colorList

logGeneral =[]
allFirstStartTime=[]
allLastEndTime=[]
fileNames=[]
files=[]
LogFileName=[]
StageName=[]
StageNameforGraph=[]
StageTaskStart=[]
StageTaskEnd=[]

sameColor=[]

class GeneralLog:

    def readCsvtoList(configPath):
        
        filename = open(configPath+r'\Config.csv', 'r')
    
        # creating dictreader object
        file = csv.DictReader(filename)
        
        # iterating over each row and append
        # values to empty list
        for col in file:
            LogFileName.append(col['LogFileName'])
            StageName.append(col['StageName'])
            StageTaskStart.append(col['StageTaskStart'])
            StageTaskEnd.append(col['StageTaskEnd'])
        # printing lists
        # print('LogFileName:', LogFileName)
        # print('StageName:', StageName)
        # print('StageTaskStart:', StageTaskStart)
        # print('StageTaskEnd:', StageTaskEnd)

    def readListtoCompareLog(filePath):
        
        for j in range (len(LogFileName)):
            k=1
            if LogFileName[j] in filePath:
                    with open(filePath) as f:
                        lines=f.readlines()
                        
                        start_line=""
                        
                        for line in lines:
                            
                            if StageTaskStart[j] in line and StageTaskStart[j]!="FILE_START":
                                                               
                                line = line.split(" ")[0]+" "+line.split(" ")[1]
                                start_line=line
           
                            elif StageTaskEnd[j] in line and StageTaskEnd[j] !="FILE_END":
                                line = line.split(" ")[0]+" "+line.split(" ")[1]
                                if LogFileName=="stackApiServer.log":
                                    StageNameforGraph.append(StageName[j]+"-Trial "+str(k))
                                    k +=1
                                    sameColor.append(colorList[j])
                                StageNameforGraph.append(StageName[j])
                                sameColor.append(colorList[j])
 
                                allLastEndTime.append(line)
                                allFirstStartTime.append(start_line)


                       
                            elif StageTaskStart[j] in line and StageTaskEnd[j]=="FILE_END":
                                logs.readLastTime(filePath)
                                sameColor.append(colorList[j])
                                break
                            elif StageTaskEnd[j] !="FILE_END" and StageTaskEnd[j] in line:
                                logs.readLastTime(filePath)
                                sameColor.append(colorList[j])
                                break
                            elif StageTaskStart[j]=="FILE_START" and StageTaskEnd[j]=="FILE_END":
                                StageNameforGraph.append(StageName[j])
                                sameColor.append(colorList[j])
                                logs.readFirstTime(filePath)
                                logs.readLastTime(filePath)
                                break
            
        
        # print(sameColor)
                            
                                
                           
                                    


    def logList(path):
        with os.scandir(path) as entries:
            for f in entries:
                if f.is_file():
                    # print(f.name)
                    fileNames.append(f.name)

        return fileNames

    def readFirstTime(fileF):
        # print(fileF)
        for line in list(open(fileF)):
            # if fileF.__contains__("commissioning.log"): #or fileF.__contains__("stackApiServer.log"):
                # files.append(fileN)
           
            
            # first_line = first_line.split(" ")[0]+" "+first_line.split(" ")[1]
            # allFirstStartTime.append(first_line)
            try:
                
                line = line.split(" ")[0]+" "+line.split(" ")[1]
                datetime.strptime(line,'%Y-%m-%d %H:%M:%S.%f')
                # print(line)
                allFirstStartTime.append(line)
                break     
            except:
                    nullcontext
      
    def readLastTime(fileF):
        # print(fileF)
        # if fileF.__contains__("commissioning.log"):# or fileF.__contains__("stackApiServer.log"):
        for line in reversed(list(open(fileF))):
            
            
            try:
                
                line = line.split(" ")[0]+" "+line.split(" ")[1]
                
                datetime.strptime(line,'%Y-%m-%d %H:%M:%S.%f')
                # print(line)
                allLastEndTime.append(line)
                break       
            except:
                    nullcontext
       
    def getVariable(fig1_xstart,fig1_xend,fig1_y_axis,fig1_filter,fig1_vertical_line,fig1_allFirstStartTime,newDir,taskData,filePath,durationList,duration_Threshold,path):
        runRafLogReaderGeneral(path)
        figCreate(fig1_xstart,fig1_xend,fig1_y_axis,fig1_filter,fig1_vertical_line,fig1_allFirstStartTime,allFirstStartTime,allLastEndTime,StageNameforGraph,newDir,taskData,filePath,durationList,duration_Threshold,sameColor)
        

logs=GeneralLog

def runRafLogReaderGeneral(path):
    
    fileNames=logs.logList(path)
    
    fileFormatName=['commissioning','configure','main-migration-primary','main-migration-secondary','stackApi','vnfr-upgrade-mini','vnfr-mini-playbook','ansible_output']
    # print(fileNames)
    fileCount=0
    csvPath=path.split("UpdatedTimeLogs")[0]
    logs.readCsvtoList(csvPath)
    for i in fileNames:
        if any(x in str(i) for x in fileFormatName):
            file=path+"/"+str(i)
            # print(file)
            NEName=str(i).split("-")
             
            # print(NEName)
            fileCount +=1
            # logs.readFirstTime(file,str(i))
            # logs.readLastTime(file)
            logs.readListtoCompareLog(file)
       
        else:
            print("Skipping for : "+str(i))
    
    

