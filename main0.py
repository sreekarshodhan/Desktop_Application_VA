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
		query = r.recognize_google(audio, language ='en-in')
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
        row = (task, '0' , date,)

        cursor.execute(query, row)
        db.commit()
        self.updateTaskList(date)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
    