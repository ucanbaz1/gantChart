from cgitb import text
from contextlib import nullcontext
from tkinter import W, font
import threading
from turtle import color
from typing import Text
import PySimpleGUI as sg
from fileReaderv3 import runFileReader
from RAF_Log_Reader import runRafLogReader
from StageTaskReader import getInputPath
import subprocess
import sys

import webbrowser


class GanttChartGUI:

    def createGUI():
        # sg.T("GanttChart", justification="center",expand_x=True, font=('Courier New', 25), enable_events=True)
        
        
        sg.theme("LightGrey1")
        layout = [  [sg.Image(filename='ribbon.png', size=(66,60)),sg.Image(filename='timeline.png', size=(500,100))],
                    [sg.Checkbox("",default=False , key="-1-"), sg.T("ConfigReader:", s=10, justification="r"),sg.I(key="-Config-"), sg.FileBrowse()],
                    [sg.Checkbox("",default=False, key="-2-"),sg.T("FileReader:", s=10, justification="r"), sg.I(key="-File-"), sg.FolderBrowse()],
                    [sg.Checkbox("",default=True, key="-3-"),sg.T("LogReader:", s=10, justification="r"), sg.I(key="-Log-"), sg.FolderBrowse()],
                    [sg.T(' ', s=36, justification="r")],
                    [sg.T('Show process duration > (in sec):', s=36, justification="r"), sg.I(key="-Time-",size=(21))],
                    [sg.T('Time difference between Container and Lab NTPs:', s=36,  justification="r"), sg.I(key="-TD-",default_text='00:00:00.000',size=(21))],
                    [sg.T(' ', s=36, justification="r")],
                    [sg.T("Console Output", justification="left", expand_x=True, font=('Courier New', 10), enable_events=True)],
                    # [sg.Output(size=(80,15))],
                    [sg.T(' ', s=36, justification="r")],
                    [sg.Exit(s=16, button_color="#bf6464"),sg.Button("Run", s=16, key="-run-")],
                    [sg.T("URL:"),sg.Text('GanttChart', justification="l", expand_x=True, font=('Courier New', 16), enable_events=True, key='-url-')],]
                

        window= sg.Window("GanttChart",layout,finalize=True, icon=r'icon.ico')
       

        
    
        while True:
                event, values = window.read(timeout=500)
                
   
                if event in (sg.WINDOW_CLOSED,"Exit"):
                    break
                if event in  ("-run-"):                                   
                    gui.runCommand(cmd=values['-Log-'], window=window)
                    if window[event].get_text() != "Running":
                        window["-run-"].update(text="Running")  
                        sg.popup("Click Ok to Run")
                        
                        if window[event].get_text() != "Running":
                            window["-run-"].update(text="Running")  
                            sg.popup("Click Ok to Run")
                        if values["-1-"] ==True:
                            if values["-Config-"] =="":
                                sg.popup("Config Path Undefined!")
                            else:
                                getInputPath(values["-Config-"])
                                sg.popup("Done!")

                        elif values["-2-"] ==True:
                            if values["-File-"] == "" :
                                sg.popup("File Reader Path Undefined!")
                            else:
                                runFileReader(values["-File-"],values["-TD-"])
                                sg.popup("Done!")
                        
                        elif values["-3-"] ==True:
                            if values["-Log-"]=="" or values["-Time-"]=="" :
                                sg.popup("Logs Path or Time Undefined!")
                            else:
                                runRafLogReader(values["-Log-"], values["-Time-"])
                                sg.popup("Done!")

                        elif values["-2-"] ==True and values["-3-"] ==True:
                            if values["-File-"] != "" and values["-Time-"] !="" and values["-Log-"]!="":
                                runFileReader(values["-File-"],values["-TD-"])
                                runRafLogReader(values["-Log-"],values["-Time-"])
                                sg.popup("Done!")

                        window["-run-"].update(text="Run") 
                        
                            
                        url=values["-Log-"]+"\\GanntFiles\\GanttChart_Task_Overview.html"
                        window["-url-"].update(font=('Courier New', 16, 'underline'),text_color='blue')
                elif  event in ("-url-"):
                        try:
                            webbrowser.open(url)
                        except:
                            nullcontext                    
                
        window.close()
    def runCommand(cmd, timeout=None, window=None):
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ''
        for line in p.stdout:
            line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
            output += line
            print(line)
            window.Refresh() if window else None        # yes, a 1-line if, so shoot me
        retval = p.wait(timeout)
        return (retval, output)      


    # if __name__ == '__main__':
    #     createGUI()
gui = GanttChartGUI
