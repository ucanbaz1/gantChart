"""
File Reader V3
Created by Ersin YAYLA
V3: Updated the time jump catching and time updating metods
"""
"""
To Do  List:
- Configure files all logs will be updated due to time gap found in commisioning logs
- If there is no time gap, skip the updating 
"""


import plotly.express as px
import plotly
import pandas
from datetime import datetime,timedelta
import os
from dateutil.parser import parse
import ctypes, sys
import re

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def makeDirectory(path):
    newPath = path + "\\" + "UpdatedTimeLogs"
    try:
        os.mkdir(newPath)
    except FileExistsError as exc:
        print(exc)
    return newPath

def logList(path):
    fileNames=[]
    with os.scandir(path) as entries:
        for f in entries:
            if f.is_file():
                print(f.name)
                fileNames.append(f.name)
    print(fileNames)
    return fileNames


def is_date(string, fuzzy=True):
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

def startEndDateExtractor(filePath,filename):
    file=filePath+"\\"+filename
    i=-1
    dateFormat = '^20[0-9]+\-[01][0-9]\-[0-3][0-9]'
    while True:
            with open(file, "r") as f:
                firstDateCandidate=f.readline()
                firstDate=firstDateCandidate.split(" ")[0]+" "+firstDateCandidate.split(" ")[1]
                lastDateCandidate=f.readlines()[i]
                startsWithDateCheck = re.search(dateFormat, lastDateCandidate)
                if startsWithDateCheck:
                    print(" There is date ")
                    lastDate=lastDateCandidate.split(" ")[0]+" "+lastDateCandidate.split(" ")[1]
                    with open(filePath + "\\UpdatedTimeLogs\\mileStones.txt", "a") as mf:
                        mf.write(filename + ";" + firstDate + ";" + lastDate+"\n")
                        mf.close()
                    break
                else:
                    print("there is no date")
                f.close()
            i-=1

def clockChecker(file):
    fileStartEndDate=[]
    with open(file) as f:
        lines=f.readlines()
        lineNumber = 1
        taskLineNumber=0
        targetLineNumber = 0
        listofLineNumbers=[]
        

        for line in lines:
            if is_date(str(line.split(" ")[0])):
                if "n=ansible | PLAY RECAP ***" in line:
                    print("We are at the end of file : " + file)
                    break
                #elif "Run chronyd with tmp NTP conf file to set system clock" in line:
                elif "Run chronyd with primary NTP IP" or "Run chronyd with tmp NTP conf file to set system clock" in line:
                    if "ERROR" in line:
                        continue
                    else:
                        targetLineNumber = lineNumber + 3
                        taskLineNumber = lineNumber
                        taskLineDate= str(line.split(" ")[0]+" "+line.split(" ")[1])
                        print("TASK Line number is : "+str(lineNumber)+" -> Its date is : " +taskLineDate)

                elif lineNumber == targetLineNumber:
                    #print("FOUND= " + line)
                    #print("line number is : " + str(lineNumber))
                    #timeUpdate = str(line.split(" ")[13]).strip("(").strip(")")
                    updatedDateFromNTP=str(line.split(" ")[0]+" "+line.split(" ")[1])
                    print("Time is {} but it should be {}. So updating accordingly !!!!! ".format(taskLineDate,updatedDateFromNTP))
                    if datetime.strptime((updatedDateFromNTP), '%Y-%m-%d %H:%M:%S,%f') > datetime.strptime((taskLineDate), '%Y-%m-%d %H:%M:%S,%f'):
                        timeUpdate=datetime.strptime((updatedDateFromNTP), '%Y-%m-%d %H:%M:%S,%f')-datetime.strptime((taskLineDate), '%Y-%m-%d %H:%M:%S,%f')
                        timeUpdate = str(timeUpdate).rstrip("000")
                    else:
                        timeUpdate=datetime.strptime((taskLineDate), '%Y-%m-%d %H:%M:%S,%f')-datetime.strptime((updatedDateFromNTP), '%Y-%m-%d %H:%M:%S,%f')
                        timeUpdate = "-"+str(timeUpdate).rstrip("000")
                    timeUpdate=str(timeUpdate)
                    print("Time difference is : "+timeUpdate)
                    targetLineNumber = 0
                    if (float(timeUpdate.split(":")[2]) > 1):
                        listofLineNumbers.append(str(taskLineNumber) + ";" + timeUpdate)
                    print(listofLineNumbers)
                else:
                    pass
            lineNumber += 1
        f.close()

    print(listofLineNumbers)
    return listofLineNumbers


def clockUpdater(file,listofNumbers,newFile):
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(listofNumbers)
    print(file)
    print(newFile)

    with open(file,"r") as f:
        lines = f.readlines()
        lineNumber=0
        for line in lines:
            if re.search("^[a-zA-Z]", line) or line.startswith('}'):
                continue
            newDate=""
            new_f = open(newFile, "a")
            if is_date(str(line.split(" ")[0])):
                old_time = str(line.split(" ")[0]) + " " + str(line.split(" ")[1]).replace(",", ".")
                print("***************************************************************************************")
                for i in range(len(listofNumbers)):

                    print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
                    minus = False
                    lineTarget=listofNumbers[i].split(";")
                    print(lineTarget)
                    if lineNumber<int(lineTarget[0])+2:
                        print("LINE : "+ str(lineNumber)+" : -> "+line)
                        timeUpdate=lineTarget[1]
                        if timeUpdate.__contains__("-"):
                            minus = True
                            timeUpdate = timeUpdate.strip("-")
                        timeUpdate = timeUpdate.replace(".", ":")
                        delta = timeUpdate.split(":")
                        print(delta)
                        print("OLD : " + old_time)
                        if minus:
                            new_time_date = datetime.strptime((old_time), '%Y-%m-%d %H:%M:%S.%f') - timedelta(
                                hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]),
                                milliseconds=int(delta[3]))

                        else:
                            new_time_date = datetime.strptime((old_time), '%Y-%m-%d %H:%M:%S.%f')+ timedelta(
                                hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]),
                                milliseconds=int(delta[3]))
                        old_time=str(new_time_date).rstrip("000")
                        if not old_time.__contains__("."):
                            old_time = old_time + ".000"

                print("NEW : " + str(old_time))
                new_f.write(old_time + " " + line)
            else:
                new_f.write( line)

            new_f.close()

            lineNumber +=1
        f.close()


filePath=input("Please enter a filename path: ")
newDir=makeDirectory(filePath)
fileNames=logList(filePath)
fileFormatName=['commissioning','configure','main-migration-primary','main-migration-secondary','stackApi','Ansible_UW','vnfr-upgrade-mini','vnfr-mini-playbook','ansible_output']
print(fileNames)

for i in fileNames:
    if any(x in str(i) for x in fileFormatName):
        file=filePath+"\\"+str(i)
#        startEndDateExtractor(filePath,str(i))
        print(file)
        NEName=str(i).split("-")
        print(NEName)
        newFile=newDir+"\\"+str(i)
        print(newFile)
        list=clockChecker(file)
        clockUpdater(file,list,newFile)
    else:
        print("Skipping for : "+str(i))

