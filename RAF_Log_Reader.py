__author__ = "Ersin YAYLA"

__version__ = "0.4"
__maintainer__ = "Ufuk CANBAZ"
__dict__ = "This project is check logs and checks their start time, end time, duration and task name. Then it creates a gantt chart figure to display its." \
           "Plotly dash has been removed. A new method added to create figure in html."

"""
__version__ = 0.4 updates :
    - converted more suitable structure for stackAPiLog and ansible_output* log files
    - GanttChart html and CSV.csv  will be created under GanttFiles in UpdatedTimeLogs directory 
"""


from datetime import datetime,timedelta
import os
import re
from ReadLogGeneral import GeneralLog
import shutil


allFirstStartTime=[]
fileNames=[]

def logList(path):
    with os.scandir(path) as entries:
        for f in entries:
            if f.is_file():
                # print(f.name)
                fileNames.append(f.name)
    # print(fileNames)
    return fileNames

# Create
def makeDirectory(path):
    if os.path.exists(path + "\GanntFiles"):
        shutil.rmtree(path + "\GanntFiles")
    newPath = path + r"\GanntFiles"
    try:
        os.mkdir(newPath)
    except FileExistsError as exc:
        print(exc)
    return newPath

def readFirstTime(fileF):
    with open(fileF) as file:
        content = file.read()
        first_line = content.split('\n', 1)[0]
        allFirstStartTime.append(first_line[0:23])
    # print(fileF)
       
def taskCollector(file,NetEName,newFile,fileCount,duration_Threshold):
    T_List=[]
    PT_List=["","","","","","","",""]
    dateAdjusted=[]
    
    with open(file) as f:
        lines=f.readlines()
        line_no=0
        dateFormat = '^20[0-9]+\-[01][0-9]\-[0-3][0-9]'
        
        
        
                       
        for line in lines:
            startsWithDateCheck = re.search(dateFormat, line)

            if  startsWithDateCheck and "TASK" in line:
                """print(PT_List)"""
                line=line.replace("*","").strip(" \n")
                line = line.replace(",", ".")
                """print("PRINT LINE: "+ line)"""
                T_List=line.split(" ",8)
               
                

                if line_no!=0:

                    compare_time_date = datetime.strptime((PT_List[0] + " " + PT_List[1]),
                                                          '%Y-%m-%d %H:%M:%S.%f') + timedelta(seconds=duration_Threshold)
                   
                    #print(PT_List[1])
                    if(compare_time_date<datetime.strptime((T_List[0] + " " + T_List[1]),
                                                          '%Y-%m-%d %H:%M:%S.%f')):

                       
                        start_time= PT_List[0].split('.')[0]+" "+PT_List[1].split('.')[0]
                        print("PTLIST1",PT_List)
                        # print(start_time)
                        end_time= T_List[0].split('.')[0]+" "+T_List[1].split('.')[0]

                        #print(PT_List[6]+" : "+start_time+"----"+end_time)
                        duration=datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
                        # print("DURATION: "+str(duration))
                        if "stackApi" in file:
                            PT_List[8]= PT_List[8].split("]")[0]+"]"
                            print("PT_List", PT_List)
                            TASKList = PT_List[0] + " " + PT_List[1] + ";" + T_List[0] + " " + T_List[
                                1] + ";" + " Duration: " + str(duration) + ";" + "stackAPI-"+ PT_List[8]
                            print("TaslList",TASKList)
                        elif "ansible_output" in file:
                            PT_List[8] = PT_List[8].split("]")[0] + "]"
                            TASKList = PT_List[0] + " " + PT_List[1] + ";" + T_List[0] + " " + T_List[
                                1] + ";" + " Duration: "+str(duration)+ ";"+NetEName + "-" + PT_List[8] 
                        else:
                            TASKList = PT_List[0] + " " + PT_List[1] + ";" + T_List[0] + " " + T_List[
                                1] + ";" + " Duration: " + str(duration) + ";" + NetEName + "-" + PT_List[8] 
                        
                        new_f=open(newFile,"a")
                        new_f.write(TASKList)
                        new_f.write(fileNames[fileCount]+"\n")
                        new_f.close()
                        
                        
                    # else:
                    #      print( "It takes less than 10 sec :"+NetEName + "-" + PT_List[8])

                else:
                    line_no = +1
                    # print("Keeping first TASK.....")
                    # print("START: "+ str(T_List))
                    



                PT_List = T_List
            elif line.__contains__("PLAY RECAP"):
                # print("End line : " +line)
                PT_List = T_List
                
            

    f.close()
    

def Gantt_plotter(textname,newDir,duration_Threshold,path):
    task=[]
    start=[]
    endTime=[]
    durationList=[]
    taskAndDuration = []
    taskData=[]
    taskFilterNames =[]
    taskFilterName=[]
    taskFilterNamesList=[]

    
    filePath = newDir + r'\CSV.csv'
    with open(textname,'r') as file:
        graphLines=file.readlines()
        for i in graphLines:
            task.append(i.split(";")[3]+" -> "+i.split(";")[2])
            # print("UFUK", task)
            start.append(i.split(";")[0])
            endTime.append(i.split(";")[1])
            

        for i in task:
            #Use of regex structure to break up some data and use it wherever we want.
            taskNameLine = re.search(r'\[(.*?)\]', i)
            taskDuration = re.search(r'(?<=->)[^.]*',i)
            taskFilterName = re.search(r'](.*)', i)
            mission = i.split('-')[0]
            
                      
            """ Commented out because it can include digit and special characters 
            for j in taskMission:
                #Parsing task names with regex in order to colorize according to task names.
                mission = re.search(r'[a-zA-Z]+', j)
                """
           
            if taskNameLine and taskDuration and taskFilterName:
                # Grouping data separated by regex
                durationGroup = taskDuration.group(0)
                taskFilterNames= taskFilterName.group(1)
                taskFilterNamesList.append(taskFilterNames)
                durationList.append(durationGroup)
                taskAndDuration.append(mission+taskNameLine.group(0)+taskDuration.group(0))
                taskData.append(mission+taskNameLine.group(0))

    file.close()

    GeneralLog.getVariable(start,endTime,taskAndDuration,taskFilterNamesList,fileNames,allFirstStartTime,newDir,taskData,filePath,durationList,duration_Threshold,path)



def runRafLogReader(path, duration_Threshold):
    

    duration_Threshold=float(duration_Threshold)
    NEName=[]
   
    newDir=makeDirectory(path)
    newFile=newDir+r"\TASKListLongerThan"+str(duration_Threshold)+"sec.txt"
    #İf file is exist delete file
    if(os.path.exists(newFile) and os.path.isfile(newFile)):
        os.remove(newFile)
    # print(newDir)
    fileNames=logList(path)
    fileFormatName=['commissioning','configure','main-migration-primary','main-migration-secondary','stackApi','vnfr-upgrade-mini','vnfr-mini-playbook','ansible_output']
    # print(fileNames)
    fileCount=0

    for i in fileNames:
        if any(x in str(i) for x in fileFormatName):
            file=path+"/"+str(i)
            # print(file)
            NEName=str(i).split("-")
            # print(NEName)
            taskCollector(file,NEName[0],newFile,fileCount,duration_Threshold)
            fileCount +=1
            readFirstTime(file)
            
        else:
            print("Skipping for : "+str(i))
    
    Gantt_plotter(newFile,newDir,duration_Threshold,path)
    
