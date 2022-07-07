from tkinter import *
import speech_recognition as sr
import pyttsx3

    

def main():
    root=Tk()
    gui=Window(root)
    gui.root.mainloop()
    return None

class Window:

    def __init__(self,root):
        self.root=root
        self.root.geometry('900x450')
        self.root.title("Notes")



        self.textspace=Text(self.root)
        self.textspace.grid(row=0, column=0)
        

        Button(self.root, text="Save", command=self.savefile).grid(row=0,column=1)
        Button(self.root, text="Open", command=self.openfile).grid(row=0,column=2)
        Button(self.root, text="Speak", command=self.speech).grid(row=0,column=3)
        pass
    
        
    def speech(self):
        r=sr.Recognizer()
        with sr.Microphone() as source:
            engine=pyttsx3.init()
            engine.say("Listening")
            engine.runAndWait()
            audio=r.listen(source)
            try:
                text = r.recognize_google(audio)
                self.textspace.insert(END,text)
            except:
                engine=pyttsx3.init()
                engine.say("sorry could not recognize what you said")
                engine.runAndWait()
        return None


       
    def savefile(self):
        savegui=Tk()
        savegui.geometry('560x50')
        filecontents=self.textspace.get(0.0, END)
        

        def writefile():
            with open(file_name.get() + '.txt','w+') as file:
                file.write(filecontents)
                file.close()
                savegui.destroy()
            return None

        Label(savegui,text="File Name").grid(row=0, column=0)
        file_name=Entry(savegui,width=40)
        file_name.grid(row=0, column=1)

        Button(savegui, text="Save", command=writefile).grid(row=0, column=2)

        return None

    def openfile(self): 
        opengui=Tk()
        opengui.geometry('560x50')

        def opennew():
            try:
                with open(file_name.get() + '.txt',"r") as file:
                    self.textspace.delete(0.0,END)
                    self.textspace.insert(0.0,file.read())
                    file.close()
                    opengui.destroy()
            except FileNotFoundError:
                file_name.delete(0.0,END)
                file_name.insert(0.0,"FILE NOT FOUND. TRY ANOTHER")
            return None


        Label(opengui,text="File Name").grid(row=0, column=0)
        file_name=Entry(opengui,width=40)
        file_name.grid(row=0, column=1)

        Button(opengui, text="Open", command=opennew).grid(row=0, column=2)

        return None

    pass

main()