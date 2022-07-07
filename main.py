from tkinter import *
import sqlite3
from parso import  parse
from win10toast import ToastNotifier
from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QMessageBox
from PyQt5.uic import loadUi
import sys
import re
from PyQt5 import QtCore

import pyttsx3

import speech_recognition as sr


root = Tk()
root.geometry('1080x720')
# add title
root.title("Three tabs")
root['bg'] = 'green'


# create canvas
def tab():
    def tab1():
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)

        username = "Siri"

        def speak(audio):
            engine.say(audio)
            engine.runAndWait()

        def takeCommand():
            r = sr.Recognizer()

            with sr.Microphone() as source:
                r.pause_threshold = 1
                audio = r.listen(source)

            try:
                query = r.recognize_google(audio, language='en-in')
                print(f"User said: {query}\n")

            except Exception as e:
                print(e)
                print("Unable to Recognize your voice.")
                return "None"

            return query

        class Window(QWidget):
            def __init__(self):
                super(Window, self).__init__()
                loadUi("main0.ui", self)
                self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)
                self.calendarDateChanged()
                self.saveButton.clicked.connect(self.saveChanges)
                self.addButton.clicked.connect(self.addNewTask)
                self.listenButton.clicked.connect(self.listenForTask)

            def calendarDateChanged(self):
                print("The calendar date was changed.")
                dateSelected = self.calendarWidget.selectedDate().toPyDate()
                print("Date selected:", dateSelected)
                self.updateTaskList(dateSelected)

            def updateTaskList(self, date):
                self.listWidget.clear()

                db = sqlite3.connect("data.db")
                cursor = db.cursor()

                query = "SELECT task, completed FROM tasks WHERE date = ?"
                row = (date,)
                results = cursor.execute(query, row).fetchall()
                for result in results:
                    item = QListWidgetItem(str(result[0]))
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                    if result[1] == 1:
                        item.setCheckState(QtCore.Qt.Checked)
                    elif result[1] == 0:
                        item.setCheckState(QtCore.Qt.Unchecked)
                    self.listWidget.addItem(item)

            def saveChanges(self):
                db = sqlite3.connect("data.db")
                cursor = db.cursor()
                date = self.calendarWidget.selectedDate().toPyDate()

                for i in range(self.listWidget.count()):
                    item = self.listWidget.item(i)
                    task = item.text()
                    if item.checkState() == QtCore.Qt.Checked:
                        query = "UPDATE tasks SET completed = '1' WHERE task = ? AND date = ?"
                    else:
                        query = "UPDATE tasks SET completed = '0' WHERE task = ? AND date = ?"
                    row = (task, date,)
                    cursor.execute(query, row)

                    db.commit()

                    messageBox = QMessageBox()
                    messageBox.setText("Changes saved.")
                    messageBox.setStandardButtons(QMessageBox.Ok)
                    messageBox.exec()

            def addNewTask(self):
                db = sqlite3.connect("data.db")
                cursor = db.cursor()

                newTask = str(self.taskLineEdit.text())
                date = self.calendarWidget.selectedDate().toPyDate()

                query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
                row = (newTask, 0, date,)

                cursor.execute(query, row)
                db.commit()
                self.updateTaskList(date)
                self.taskLineEdit.clear()

            def listenForTask(self):
                speak("Listening")
                query = takeCommand().lower()

                if 'task list' in query:
                    self.parsingToAdd(query)
                    print("Adding to the tasklist")
                else:
                    print("Error couldn't add to tasklist")

            def parsingToAdd(self, query):
                common_tasks = ["shopping", "review code", "groceries", "drink water", "finish project"]
                for task in common_tasks:
                    if task in query:
                        self.parseAddNewTask(task)

            def parseAddNewTask(self, task):
                db = sqlite3.connect("data.db")
                cursor = db.cursor()
                date = self.calendarWidget.selectedDate().toPyDate()
                query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
                row = (task, '0', date,)

                cursor.execute(query, row)
                db.commit()
                self.updateTaskList(date)

        if __name__ == "__main__":
            app = QApplication(sys.argv)
            window = Window()
            window.show()
            sys.exit(app.exec())
        tab()

    def tab2():
        def main():
            root = Tk()
            gui = Window(root)
            gui.root.mainloop()
            return None

        class Window:

            def __init__(self, root):
                self.root = root
                self.root.geometry('900x450')
                self.root.title("Notes")

                self.textspace = Text(self.root)
                self.textspace.grid(row=0, column=0)

                Button(self.root, text="Save", command=self.savefile).grid(row=0, column=1)
                Button(self.root, text="Open", command=self.openfile).grid(row=0, column=2)
                Button(self.root, text="Speak", command=self.speech).grid(row=0, column=3)
                pass

            def speech(self):
                r = sr.Recognizer()
                with sr.Microphone() as source:
                    engine = pyttsx3.init()
                    engine.say("Listening")
                    engine.runAndWait()
                    audio = r.listen(source)
                    try:
                        text = r.recognize_google(audio)
                        self.textspace.insert(END, text)
                    except:
                        engine = pyttsx3.init()
                        engine.say("sorry could not recognize what you said")
                        engine.runAndWait()
                return None

            def savefile(self):
                savegui = Tk()
                savegui.geometry('560x50')
                filecontents = self.textspace.get(0.0, END)

                def writefile():
                    with open(file_name.get() + '.txt', 'w+') as file:
                        file.write(filecontents)
                        file.close()
                        savegui.destroy()
                    return None

                Label(savegui, text="File Name").grid(row=0, column=0)
                file_name = Entry(savegui, width=40)
                file_name.grid(row=0, column=1)

                Button(savegui, text="Save", command=writefile).grid(row=0, column=2)

                return None

            def openfile(self):
                opengui = Tk()
                opengui.geometry('560x50')

                def opennew():
                    try:
                        with open(file_name.get() + '.txt', "r") as file:
                            self.textspace.delete(0.0, END)
                            self.textspace.insert(0.0, file.read())
                            file.close()
                            opengui.destroy()
                    except FileNotFoundError:
                        file_name.delete(0.0, END)
                        file_name.insert(0.0, "FILE NOT FOUND. TRY ANOTHER")
                    return None

                Label(opengui, text="File Name").grid(row=0, column=0)
                file_name = Entry(opengui, width=40)
                file_name.grid(row=0, column=1)

                Button(opengui, text="Open", command=opennew).grid(row=0, column=2)

                return None

            pass

        main()
        tab()

    def tab3():
        ct1 = Canvas(root, bg="light green", width=1500, height=800)
        ct1.place(x=1, y=1)
        label3 = Label(root, text="This is task scheduling", bg="light green", font=("Arial", 30))
        label3.place(x=300, y=300)
        Speak_b = Button(root, text="Speak", font=('poppins', 15))
        Speak_b.place(x=500, y=500)
        tab()

    c1 = Canvas(root, bg='brown', width=1500, height=50)
    c1.place(x=1, y=20)
    tab1_b = Button(root, text='Remainder App', font=('Arial', 10), command=tab1)
    tab1_b.place(x=150, y=35)
    tab1_b = Button(root, text='NoteTaking App', font=('Arial', 10), command=tab2)
    tab1_b.place(x=450, y=35)
    tab1_b = Button(root, text='Task Scheduler App', font=('Arial', 10), command=tab3)
    tab1_b.place(x=750, y=35)


Speak_b = Button(root, text="Speak", font=('poppins', 15))
Speak_b.place(x=500, y=500)

tab()
root.mainloop()
