from cgi import print_form
from fileinput import filename
import imp
from pydoc import visiblename
from turtle import color, fillcolor
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os





colorList = ["yellow","red","blue","orange","green","gold","skyblue","gray","pink","indigo","blueviolet","burlywood", "purple","aqua","aquamarine",
            "seagreen","sienna","plum","royalblue","salmon","silver","lightgoldenrodyellow","darkslategray","darkolivegreen",
			"cadetblue","coral","cornflowerblue","crimson","cyan","turquoise","lightslategrey","cornsilk","firebrick",
			"darkcyan","grey","peru","darkorange","rebeccapurple","moccasin","dodgerblue","lightsalmon",
            "darkgoldenrod","darkgrey","darkgreen","darkmagenta","tomato",
           "darkred","deepskyblue","forestgreen","fuchsia","slategrey","lavender",
            "lavenderblush","lawngreen","seashell","palegoldenrod","rosybrown",
           "lightseagreen","lime","magenta","maroon","mediumvioletred","olive","yellow","red","blue","orange","green","gold","skyblue","gray","pink","indigo","blueviolet","burlywood", "purple","aqua","aquamarine",
            "seagreen","sienna","plum","royalblue","salmon","silver","lightgoldenrodyellow","darkslategray","darkolivegreen",
            ]

def figCreate(fig1_xstart,fig1_xend,fig1_y_axis,fig1_filter,fig1_vertical_line,fig1_allFirstStartTime,fig2_xstart,fig2_xend,fig2_y_axis,newDir,taskData,durationList,duration_Threshold,sameColor,DurationList):
    
      
    fig1 = createFigure(fig1_xstart,fig1_xend,fig1_y_axis,fig1_filter,fig1_vertical_line,fig1_allFirstStartTime,colorList,True)
    fig2= createTableFig(fig1_xstart,fig1_xend,newDir,taskData,durationList,True)
    fig3 = createFigure(fig2_xstart,fig2_xend,fig2_y_axis,fig2_y_axis,fig2_y_axis,fig2_xstart,sameColor,False)
    fig4=createTableFig(fig2_xstart,fig2_xend,newDir,fig2_y_axis,DurationList,False)

        #Get parameters for create hmtl page of gantt chart
    figures_to_html([fig3,fig4,fig1,fig2],"Task Overview","NOTE: This gantt chart shows tasks running over " +str(duration_Threshold)+" seconds!",newDir+r"\GanttChart_Task_Overview.html")
    
def createTableFig(start,endTime,newDir,taskData,durationList,tableType):

    if tableType==True:
        pathName='\CSV.csv'
    else:
        pathName='\Stage.csv'
    
    filePath=newDir+pathName
    data = {'Task': taskData, 'Start': start, 'Finish': endTime, 'Duration':durationList}
    # if (os.path.exists(filePath) and os.path.isfile(filePath)):
    #     os.remove(filePath)
    df = pd.DataFrame(data)
    df.to_csv(filePath)

    # Creating a table in dash with CSV file
    df = pd.read_csv(newDir+pathName, index_col=0)
    # df.sort_values(df.columns[3], 
    #                 axis=0,
    #                 inplace=False)
    
    fig2 = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.Task, df.Start, df.Finish, df.Duration],
                   fill_color='lavender',
                   align='left'))
    ])
    return fig2

    #Create gantt chart figure.
def createFigure(start,endTime,taskAndDuration,taskFilterNamesList,fileNames,allFirstStartTime,color,gantType):   
       
    fig=px.timeline(x_start=start,x_end=endTime,y=taskAndDuration,color=taskFilterNamesList,color_discrete_sequence=color)

    taskCount=0
    colorCount=0
    vlineCount= []
    
    
    if gantType ==True:
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
   
    if gantType==True:
        fig.update_layout(
            
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            
            #C:\Users\ucanbaz\Desktop\Logs\UpdatedTimeLogs
            #disable and ebable buttons for filter tasks
            
            updatemenus=[
                
                dict(
                buttons=list([
                    
                    dict(
                        args=[{"visible":['legendonly']},
                            {'shapes[{}].visible'.format(i): False for i in vlineCount}],
                        label="Option1",
                        method="update"
                    ),
                    dict(
                        args=[{"visible":[True]},
                            {'shapes[{}].visible'.format(i): False for i in range(colorCount)}],
                        label="Option2",
                        method="update"
                    ),
                    dict(
                        args=[{"visible":[True]},
                            {'shapes[{}].visible'.format(i): False for i in vlineCount}],
                        label="Option3",
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
    else:
        fig.update_layout(
            
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
            
            #C:\Users\ucanbaz\Desktop\Logs\UpdatedTimeLogs
            #disable and ebable buttons for filter tasks
            
            updatemenus=[

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


    return fig

    #
def figures_to_html(figs, header, note, filename):
    
    dashboard = open(filename, 'w')
        
    dashboard.write("<html><head></head><body>" + "\n")
    dashboard.write("<h1 style=\"text-align:center;font-size:40;\">"+header+"</h1>"+"\n")
    dashboard.write("<p style=\"color:red\"><strong>" + note + "</strong></p>" + "\n")
    dashboard.write("<p style=\"color:red\"><small>Option1: Removes all time line and just shows vertical lines</small></p>" + "\n")
    dashboard.write("<p style=\"color:red\"><small>Option2: Removes all vertical lines</small></p>" + "\n")
    dashboard.write("<p style=\"color:red\"><small>Option3: Removes vertical lines which far from other vertical lines</small></p>" + "\n")
        #dashboard.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><style>.vl {border-left: 4px solid green;height: 75px;position: absolute;left: 13%;margin-left: -3px;top: 100;}</style></head><body><h2>"+mgStart+"</h2><div class=\"vl\"></div>")
        #dashboard.write("<br><p><strong>" + mgTime + "</strong></p>")
    for fig in figs:
        inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
        dashboard.write(inner_html)
    dashboard.write("</body></html>" + "\n")


