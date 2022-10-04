from cgitb import text
from tkinter import W
from typing import Text
import PySimpleGUI as sg
from fileReaderv3 import runFileReader
from RAF_Log_Reader import runRafLogReader
from StageTaskReader import getInputPath

import webbrowser


class GanttChartGUI:
    
    def createGUI(self):
        
        
        sg.theme("BlueMono")
        layout = [  
                    [sg.T("GanttChart", justification="center", expand_x=True, font=('Courier New', 25), enable_events=True)],
                    [sg.T("ConfigReader:", s=15, justification="r"), sg.I(key="-Config-"), sg.FileBrowse()],
                    [sg.T("FileReader:", s=15, justification="r"), sg.I(key="-File-"), sg.FolderBrowse()],
                    [sg.T("LogReader:", s=15, justification="r"), sg.I(key="-Log-"), sg.FolderBrowse()],
                    [sg.T('Time:', s=15, justification="r"), sg.I(key="-Time-",size=(21))],
                    [sg.T('TimeDifference:', s=15, justification="r"), sg.I(key="-TD-",size=(21))],
                    [sg.Exit(s=16, button_color="#bf6464"),sg.Button("Run", s=16, key="-run-")],
                    [sg.T("URL:"),sg.Text('GanttChart', justification="l", expand_x=True, font=('Courier New', 16, 'underline'), enable_events=True, key='-url-')],]
                
        window= sg.Window("GanttChart",layout,finalize=True,grab_anywhere=True, no_titlebar=True)
        
    
        while True:
                event, values = window.read()
                
   
                if event in (sg.WINDOW_CLOSED,"Exit"):
                    break
                if event in  ("-run-"):                                   
                
                    if values["-File-"] =="" and values["-Log-"]=="" or values["-Log-"]!="" and values["-Time-"]=="" :
                        sg.popup("Logs Path or Time Undefined!")
                    elif values["-File-"] != "" and values["-Time-"] !="" and values["-Log-"]=="":
                        sg.popup("You Dont Need Time For FileReader!")
                    else:
                        if values["-Config-"] =="":
                                sg.popup("Config CSV should be created!")
                        else:
                            if window[event].get_text() != "Running":
                                window["-run-"].update(text="Running")  
                                sg.popup("Click Ok to Run")
                                
                                if values["-File-"] != "" and values["-Log-"] =="":
                                    runFileReader(values["-File-"],values["-TD-"])
                                elif values["-Log-"] !="" and values["-Time-"] !="" and values["-File-"] == "":
                                    runRafLogReader(values["-Log-"], values["-Time-"])
                                    getInputPath(values["-Config-"])
                                elif values["-File-"] !="" and values["-Log-"]!="" and values["-Time-"] !="": 
                                    runFileReader(values["-File-"],values["-TD-"])
                                    runRafLogReader(values["-Log-"],values["-Time-"])
                                    getInputPath(values["-Config-"])
                                window["-run-"].update(text="Run") 
                                sg.popup("Done!")
                            
                    url=values["-Log-"]+"\\GanntFiles\\GanttChart_Task_Overview.html"
                elif  event in ("-url-"):
                        webbrowser.open(url)
                    
        window.close()

gui=GanttChartGUI()
gui.createGUI()