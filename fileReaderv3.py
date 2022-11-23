"""
File Reader V3.1
Created by Ersin YAYLA
V3: Updated the time jump catching and time updating metods
V3.1:
- Configure logs timeline are being updated as per commisioning logs time update 
"""


from contextlib import nullcontext
import plotly.express as px
import plotly
import pandas
from datetime import datetime,timedelta
import os
from dateutil.parser import parse
import ctypes, sys
import re
import shutil


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def makeDirectory(path):
    if os.path.exists(path + "\\UpdatedTimeLogs"):
        shutil.rmtree(path + "\\UpdatedTimeLogs")
    
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

def file_len(filename):
    with open(filename) as f:
        for i, _ in enumerate(f):
            pass
    return i+1
def lineSplit(line,file):
    if file=="stackApiServer.log":
     
        line=line.split("T")[0]+" "+line.split("T")[1]
        
    else:
       
        line=line.split(" ")[0]+" "+line.split(" ")[1]
    return line

def startEndDateExtractor(filePath,filename):
    file=filePath+"\\"+filename
    i=-1
    dateFormat = '^20[0-9]+\-[01][0-9]\-[0-3][0-9]'
    while True:
            with open(file, "r") as f:
                firstDateCandidate=f.readline()
                firstDate=lineSplit(firstDateCandidate,file)
                lastDateCandidate=f.readlines()[i]
                startsWithDateCheck = re.search(dateFormat, lastDateCandidate)
                if startsWithDateCheck:
                    print(" There is date ")
                    lastDate=lineSplit(lastDateCandidate,file)
                    with open(filePath + "\\UpdatedTimeLogs\\mileStones.txt", "a") as mf:
                        mf.write(filename + ";" + firstDate + ";" + lastDate+"\n")
                        mf.close()
                    break
                else:
                    print("there is no date")
                f.close()
            i-=1

def clockChecker(file,fileName):
    fileStartEndDate=[]
    with open(file) as f:
        lines=f.readlines()
        lineNumber = 1
        taskLineNumber=0
        targetLineNumber = 0
        listofLineNumbers=[]
        
        for line in lines:
            if f =="stackApiServe.log":
                beforeZeroLine=str(line.split("T")[0])
                dateType="%Y-%m-%d %H:%M:%S.%f"
            else:
                beforeZeroLine=str(line.split(" ")[0])
                dateType="%Y-%m-%d %H:%M:%S,%f"
            if is_date(beforeZeroLine):
                if "n=ansible | PLAY RECAP ***" in line:
                    print("We are at the end of file : " + file)
                    break
                elif "Run chronyd with tmp NTP conf file to set system clock" in line:
                #elif "Run chronyd with primary NTP IP" or "Run chronyd with tmp NTP conf file to set system clock" in line:
                    if "ERROR" in line:
                        continue
                    else:
                        targetLineNumber = lineNumber + 3
                        taskLineNumber = lineNumber
                        taskLineDate= str(lineSplit(line,fileName))
                        print("TASK Line number is : "+str(lineNumber)+" -> Its date is : " +taskLineDate)

                elif lineNumber == targetLineNumber:
                    #print("FOUND= " + line)
                    #print("line number is : " + str(lineNumber))
                    #timeUpdate = str(line.split(" ")[13]).strip("(").strip(")")
                    updatedDateFromNTP=str(lineSplit(line,fileName))
                    print("Time is {} but it should be {}. So updating accordingly !!!!! ".format(taskLineDate,updatedDateFromNTP))
                    if datetime.strptime((updatedDateFromNTP), dateType) > datetime.strptime((taskLineDate), dateType):
                        timeUpdate=datetime.strptime((updatedDateFromNTP), dateType)-datetime.strptime((taskLineDate), dateType)
                        timeUpdate = str(timeUpdate).rstrip("000")
                    else:
                        timeUpdate=datetime.strptime((taskLineDate), dateType)-datetime.strptime((updatedDateFromNTP), dateType)
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


def clockUpdater(file,listofNumbers,newFile,fileName):
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(listofNumbers)
    print(file)
    print(newFile)
    lineTarget=listofNumbers[0].split(";")
    print(lineTarget)
    with open(file,"r") as f:
        lines = f.readlines()
        lineNumber=0
        count =1
        
        for line in lines:
            if re.search("^[a-zA-Z]", line) or line.startswith('}'):
                continue
            newDate=""
            try:
                if fileName =="stackApiServer.log":
                    dateType="%Y-%m-%d %H:%M:%S.%f"
                    lineDate=line.split("T")[0]
                    lines=line.split("T")[0]+" "+line.split("T")[1]
                    lines=lines.split(" ")[0]+" "+lines.split(" ")[1]
                else:
                    lineDate=line.split(" ")[0]
                    dateType="%Y-%m-%d %H:%M:%S.%f"
                    lines=line.split(" ")[0]+" "+line.split(" ")[1]
            except:
                nullcontext
            new_f = open(newFile, "a")
            if is_date(str(lineDate)) and lineDate.startswith("2022"):
                old_time = str(lines).replace(",", ".")
                print("***************************************************************************************")
                for i in range(len(listofNumbers)):
                    
 
                    if line.__contains__("Run chronyd with tmp NTP conf file to set system clock") and int(lineTarget[0])-12< count < int(lineTarget[0])+12: 
                        print("UFUK",count)
                        lineTarget[0]=count
                        # listofNumbers = count
                       
                    print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
                    minus = False
                    
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
                            new_time_date = datetime.strptime((old_time), dateType) - timedelta(
                                hours=int(delta[0]), minutes=int(delta[1]), seconds=int(delta[2]),
                                milliseconds=int(delta[3]))

                        else:
                            new_time_date = datetime.strptime((old_time), dateType)+ timedelta(
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
            count += 1
            lineNumber +=1
        f.close()


def runFileReader(filePath,continerDateGap):  
    continerDateGap=str(continerDateGap)
    newDir=makeDirectory(filePath)
    fileNames=logList(filePath)
    # 'vnfr-upgrade-mini','vnfr-mini-playbook',
    #fileFormatName=['commissioning','main-migration-primary','main-migration-secondary','stackApi']
    fileFormatName=['commissioning','main-migration-primary','main-migration-secondary','stackApi','Ansible_UW','ansible_output']
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
            if str(i).startswith("main") or str(i).startswith("stack"):
                list=[]
                with open(file, "r") as fp:
                    size = len(fp.readlines())
                    list.append(str(size-2)+";"+continerDateGap)
                    fp.close()
                print("It is stack or ansible file and list is : "+str(list))
                clockUpdater(file, list, newFile,str(i))
            else:
                list=clockChecker(file,str(i))
                clockUpdater(file,list,newFile,str(i))
                configure_file=str(i).strip("commissioning.log")+"configure.log"
                file=filePath+"\\"+configure_file
                newFile = newDir + "\\" + configure_file
                configure_line_count=file_len(file)
                configure_list=[]
                for t in list:
                    configure_list.append(str(configure_line_count)+";"+t.split(";")[1])
                print(configure_list)
                clockUpdater(file, configure_list, newFile,str(i))

        else:
            if "configure" in str(i):
                print("{} should have been handled already based on its commissioning log".format(str(i)))
            else:
                print("Skipping for {} since it is not in the list".format(str(i)))
