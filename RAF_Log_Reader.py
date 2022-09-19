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

from cgi import print_form
from fileinput import filename
from pydoc import visiblename
from tkinter.tix import TList
from turtle import color, fillcolor
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime,timedelta
import numpy as np
import os
import re

fileCount=0
allFirstStartTime=[]
path=input("Please add the log directory path: ")
duration_Threshold=float(input("Please define a threshold in seconds which this script will take only more than it > "))
fileNames=[]
def logList(path):
    with os.scandir(path) as entries:
        for f in entries:
            if f.is_file():
                print(f.name)
                fileNames.append(f.name)
    print(fileNames)
    return fileNames

# Create
def makeDirectory(path):
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
    print(fileF)
       
def taskCollector(file,NetEName,newFile,fileCount):
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
                        print(start_time)
                        end_time= T_List[0].split('.')[0]+" "+T_List[1].split('.')[0]

                        #print(PT_List[6]+" : "+start_time+"----"+end_time)
                        duration=datetime.strptime(end_time,'%Y-%m-%d %H:%M:%S') - datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S')
                        print("DURATION: "+str(duration))
                        if "stackApi" in file:
                            PT_List[8]= PT_List[8].split("]")[0]+"]"
                            TASKList = PT_List[0] + " " + PT_List[1] + ";" + T_List[0] + " " + T_List[
                                1] + ";" + " Duration: " + str(duration) + ";" + "stackAPI-"+PT_List[5]+ "-" + PT_List[8]
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
                        
                        
                    else:
                        print( "It takes less than 10 sec :"+NetEName + "-" + PT_List[8])

                else:
                    line_no = +1
                    print("Keeping first TASK.....")
                    print("START: "+ str(T_List))
                    



                PT_List = T_List
            elif line.__contains__("PLAY RECAP"):
                print("End line : " +line)
                PT_List = T_List
                
            

    f.close()
    

def Gantt_plotter(textname,newDir):
    task=[]
    start=[]
    endTime=[]
    durationList=[]
    taskMission=[]
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

    #Creating CSV file format by used data from the log file.
    data = {'Task': taskData, 'Start': start, 'Finish': endTime, 'Duration':durationList}
    if (os.path.exists(filePath) and os.path.isfile(filePath)):
        os.remove(filePath)
    df = pd.DataFrame(data)
    df.to_csv(filePath)

    colorList = ["yellow","red","blue","orange","green","gold","skyblue","gray","pink","indigo","blueviolet","burlywood", "purple","aqua","aquamarine",
            "seagreen","sienna","plum","royalblue","salmon","silver","lightgoldenrodyellow","darkslategray","darkolivegreen",
			"cadetblue","coral","cornflowerblue","crimson","cyan","turquoise","lightslategrey","cornsilk","firebrick",
			"darkcyan","grey","peru","darkorange","rebeccapurple","moccasin","dodgerblue","lightsalmon",
            "darkgoldenrod","darkgrey","darkgreen","darkmagenta","tomato",
           "darkred","deepskyblue","forestgreen","fuchsia","slategrey","lavender",
            "lavenderblush","lawngreen","seashell","palegoldenrod","rosybrown",
           "lightseagreen","lime","magenta","maroon","mediumvioletred","olive",
            ]

    #Create gantt chart figure.
    fig=px.timeline(x_start=start,x_end=endTime,y=taskAndDuration,color=taskFilterNamesList,color_discrete_sequence=colorList)
    
    taskCount=0
    colorCount=0
    vlineCount= []
    

    
    while taskCount < len(fileNames): 
        if fileNames[taskCount] in  taskFilterNamesList:
            fig.add_trace(go.Scatter(x=[allFirstStartTime[taskCount]],  y=['Starts'],
                            mode='lines+markers',
                            line=dict(color=colorList[colorCount]),
                            marker=dict(color=colorList[colorCount]),
                            name=fileNames[taskCount]))
            if fileNames[taskCount] == 'em1s1_vnfr-mini-playbook.log' or fileNames[taskCount] == 'em1s2_vnfr-mini-playbook.log':
                vlineCount.append(colorCount)
            fig.add_vline(x=allFirstStartTime[taskCount],  line_width=2,line_color=colorList[colorCount],y0=0,visible=True)
            colorCount +=1
        taskCount += 1
        


    fig.update_yaxes(autorange='reversed', title='Tasks')
    fig.update_xaxes(title='Time')
   
   

    fig.update_layout(
        
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        
        #C:\Users\ucanbaz\Desktop\Logs\UpdatedTimeLogs
        #disable and ebable buttons for filter tasks
        updatemenus=[
            dict(
            buttons=list([
                dict(
                    args=[{"visible":[True]},
                        {'shapes[{}].visible'.format(i):True for i in range(colorCount)},
                        # {'shapes[{}].visible'.format(i): False for i in vlineCount}
                         ],
                    label="VLine",
                    method="update"
                ),
                dict(
                    args=[{"visible":[True]},
                        {'shapes[{}].visible'.format(i): False for i in range(colorCount)}],
                    label="NonVLine",
                    method="update"
                ),
                dict(
                    args=[{"visible":[True]},
                        {'shapes[{}].visible'.format(i): False for i in vlineCount}],
                    label="NonFarVline",
                    method="update"
                )
           
            ]),
            
            type="dropdown",
                direction="down",
                active=0,
                x=0.95,
                y=1,
        ),

            dict(
                type="dropdown",
                direction="down",
                active=0,
                x=1,
                y=1,
               buttons=list([
                    dict(label="All",
                         method="update",
                         args=[{"visible":[True]},
                        {'shapes[{}].visible'.format(i):True for i in range(colorCount)}
                         
                         ]),
                    dict(label="None",
                         method="update",
                         args=[{"visible":['legendonly']},
                         {'shapes[{}].visible'.format(i): False for i in range(colorCount)}

                           ],
                         ), 
                         
                ]),
                
            )
        ],
        
        title_font_size=14,
        font_size=8,
        title_font_family='Arial'
    )
    #fig.layout.xaxis.rangeslider.visible = False  
   
    # Creating a table in dash with CSV file
    df = pd.read_csv(newDir+r'\CSV.csv', index_col=0)
    df.sort_values(df.columns[3], 
                    axis=0,
                    inplace=True)
    
    fig2 = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.Task, df.Start, df.Finish, df.Duration],
                   fill_color='lavender',
                   align='left'))
    ])
    
   

    #
    def figures_to_html(figs, header, note, filename=newDir+r"\GanttChart_Task_Overview.html"):
        dashboard = open(filename, 'w')
        
        dashboard.write("<html><head></head><body>" + "\n")
        dashboard.write("<h1 style=\"text-align:center;font-size:40;\">"+header+"</h1>"+"\n")
        dashboard.write("<p style=\"color:red\"><strong>" + note + "</strong></p>" + "\n")
        #dashboard.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>.vl {border-left: 4px solid green;height: 75px;position: absolute;left: 13%;margin-left: -3px;top: 100;}</style></head><body><h2>"+mgStart+"</h2><div class=\"vl\"></div>")
        #dashboard.write("<br><p><strong>" + mgTime + "</strong></p>")
        for fig in figs:
            inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        dashboard.write("</body></html>" + "\n")
    #Get parameters for create hmtl page of gantt chart
    figures_to_html([fig,fig2],"Task Overview","NOTE: This gantt chart shows tasks running over " +str(duration_Threshold)+" seconds!")




NEName=[]
newDir=makeDirectory(path)
newFile=newDir+r"\TASKListLongerThan"+str(duration_Threshold)+"sec.txt"
#İf file is exist delete file
if(os.path.exists(newFile) and os.path.isfile(newFile)):
  os.remove(newFile)
print(newDir)
fileNames=logList(path)
fileFormatName=['commissioning','configure','main-migration-primary','main-migration-secondary','stackApi','vnfr-upgrade-mini','vnfr-mini-playbook','ansible_output']
print(fileNames)

for i in fileNames:
    if any(x in str(i) for x in fileFormatName):
        file=path+"/"+str(i)
        print(file)
        NEName=str(i).split("-")
        print(NEName)
        taskCollector(file,NEName[0],newFile,fileCount)
        fileCount +=1
        readFirstTime(file)
        
    else:
        print("Skipping for : "+str(i))

Gantt_plotter(newFile,newDir)

