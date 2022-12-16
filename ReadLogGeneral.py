from contextlib import nullcontext
from lib2to3.pgen2.token import NAME
from datetime import datetime
import os
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
DurationList=[]
startDur=[]
endDur=[]
sortFirtTime=[]
sortLastTime=[]
sortTaskName=[]
StageNameforGraphs=[]


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

    def readListtoCompareLog(filePath):
        
        for j in range (len(LogFileName)):
            k=1
            if LogFileName[j] in filePath:
                    with open(filePath) as f:
                        lines=f.readlines()
                        
                        start_line=""
                        end_line=[]
                        for line in lines:
                            
                            if StageTaskStart[j] in line:
                                                               
                                line = line.split(" ")[0]+" "+line.split(" ")[1]
                                start_line=line
           
                            # elif StageTaskEnd[j] in line and "PLAY RECAP" in line and start_line !="":
                               
                            #         line = (line.split("To:")[1]).split(")")[0]
                            #         line2=line.split("T")[0]+" "+line.split("T")[1]
                            #         end_line.append(line2)
                            #         if end_line!="" and len(end_line)<2 :
                            #             StageNameforGraph.append(StageName[j])
                            #             sameColor.append(colorList[j])

                            #             allLastEndTime.append(line2)
                            #             allFirstStartTime.append(start_line)

                            # elif StageTaskEnd[j] in line and "endTime" in line and start_line !="":
                            #             line = ((((line.split(": ")[1]).split(",")[0]).split('"')[1]).split('"')[0])
                            #             line2=line.split("T")[0]+" "+line.split("T")[1]
                            #             end_line.append(line2)
                            #             if end_line!="" and len(end_line)<2 :
                            #                 StageNameforGraph.append(StageName[j])
                            #                 sameColor.append(colorList[j])

                            #                 allLastEndTime.append(line2)
                            #                 allFirstStartTime.append(start_line)

                                        
                            
                            elif StageTaskEnd[j] in line and start_line !="":
                                end_line.append(line.split(" ")[0]+" "+line.split(" ")[1])
                                line = line.split(" ")[0]+" "+line.split(" ")[1]
                                # if LogFileName[j]=="stackApiServer.log":
                                #     StageNameforGraph.append(StageName[j]+"-Trial "+str(k))
                                #     k +=1
                                #     sameColor.append(colorList[j])
                                
                                if "vnfr" in LogFileName[j]:

                                    if end_line!="" and len(end_line)<2 :
                                        StageNameforGraph.append(StageName[j])
                                        sameColor.append(colorList[j])
        
                                        allLastEndTime.append(line)
                                        allFirstStartTime.append(start_line)
                                else:
                                    StageNameforGraph.append(StageName[j])
                                    sameColor.append(colorList[j])
    
                                    allLastEndTime.append(line)
                                    allFirstStartTime.append(start_line)


                            elif StageTaskEnd[j]=="FILE_END" and StageTaskStart[j]!="FILE_START":
                                logs.readLastTime(filePath)
                                sameColor.append(colorList[j])
                                break
                            elif StageTaskStart[j]=="FILE_START" and StageTaskEnd[j]!="FILE_END":
                                logs.readFirstTime(filePath)
                                sameColor.append(colorList[j])
                                break
                            elif StageTaskStart[j]=="FILE_START" and StageTaskEnd[j]=="FILE_END":
                                StageNameforGraph.append(StageName[j])
                                sameColor.append(colorList[j])
                                logs.readFirstTime(filePath)
                                logs.readLastTime(filePath)
                                break


    def sortGraph():
        j=0
        for i in range(len(allFirstStartTime)):
            while j < len(allFirstStartTime):
                if datetime.strptime(allFirstStartTime[i],'%Y-%m-%d %H:%M:%S.%f')>=datetime.strptime(allFirstStartTime[j],'%Y-%m-%d %H:%M:%S.%f'):
                    StageNameforGraph.insert(i, StageNameforGraph.pop(j))
                    allFirstStartTime.insert(i, allFirstStartTime.pop(j))
                    allLastEndTime.insert(i, allLastEndTime.pop(j))
                    
                j = j+1
            j = i+1


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
            try:
                
                line = line.split(" ")[0]+" "+line.split(" ")[1]
                datetime.strptime(line,'%Y-%m-%d %H:%M:%S.%f')
                # print(line)
                allFirstStartTime.append(line)
                break     
            except:
                    nullcontext
      
    def readLastTime(fileF):
        for line in reversed(list(open(fileF))): 
            try:
                
                line = line.split(" ")[0]+" "+line.split(" ")[1]
                
                datetime.strptime(line,'%Y-%m-%d %H:%M:%S.%f')
                # print(line)
                allLastEndTime.append(line)
                break       
            except:
                nullcontext

    def getDuration():
        for i in range(len(allFirstStartTime)):
            startDur.append(allFirstStartTime[i].split('.')[0])
            endDur.append(allLastEndTime[i].split('.')[0])
            DurationList.append("Duration: "+str(datetime.strptime(endDur[i],'%Y-%m-%d %H:%M:%S')- datetime.strptime(startDur[i],'%Y-%m-%d %H:%M:%S')))
            StageNameforGraphs.append(StageNameforGraph[i]+" "+DurationList[i] )
          

    def getVariable(fig1_xstart,fig1_xend,fig1_y_axis,fig1_filter,fig1_vertical_line,fig1_allFirstStartTime,newDir,taskData,durationList,duration_Threshold,path):
        runRafLogReaderGeneral(path)
        logs.sortGraph()
        logs.getDuration()
        figCreate(fig1_xstart,fig1_xend,fig1_y_axis,fig1_filter,fig1_vertical_line,fig1_allFirstStartTime,allFirstStartTime,allLastEndTime,StageNameforGraph,newDir,taskData,durationList,duration_Threshold,sameColor,DurationList)
        

logs=GeneralLog

def runRafLogReaderGeneral(path):
    
    fileNames=logs.logList(path)
    
    fileFormatName=['commissioning','configure','main-migration-primary','main-migration-secondary','stackApi','vnfr','vnfr-mini-playbook','ansible_output']
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
            logs.readListtoCompareLog(file)
       
        else:
            print("Skipping for : "+str(i))
    
    

