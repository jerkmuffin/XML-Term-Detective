import os
import csv
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import QSound, QMultimedia, QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5 import uic



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(self.resource_path('./assets/termDetector.ui'), self)
        self.xmlDir = None
        self.csvInFile = None
        self.termList = []
        self.progressStatus = 0
        self.counter = {}
        self.outputData = ""

        self.csvBtn = self.findChild(QPushButton, 'csvSelect')
        self.csvBtn.clicked.connect(self.selectCSVFile)

        self.xmlBtn = self.findChild(QPushButton, 'xmlDirSelect')
        self.xmlBtn.clicked.connect(self.selectXMLDir)

        self.xmlLabel = self.findChild(QLabel, 'xmlDirLabel')

        self.processBtn = self.findChild(QPushButton, 'processXML')
        self.processBtn.clicked.connect(self.processXMLDir)
        self.processBtn.setEnabled(False)

        self.list = self.findChild(QListWidget, 'listWidget')

        self.progress = self.findChild(QProgressBar, 'bar')
        self.progress.setValue(self.progressStatus)
        self.progress.setVisible(False)

    def selectXMLDir(self):
        print('select dir!')
        self.xmlDir = QFileDialog.getExistingDirectory(self)
        if self.xmlDir[0] != "":
            print("selected dir: {}".format(self.xmlDir))
            print(os.listdir(self.xmlDir))
            self.xmlLabel.setText(self.xmlDir)
        self.enableProcessBtn()


    def selectCSVFile(self):
        print('select csv file!')
        self.csvInFile, _ = QFileDialog.getOpenFileName(self)
        if self.csvInFile != "":
            print("CSV File: {}".format(self.csvInFile))
            self.processCSV(self.csvInFile)
        self.enableProcessBtn()

    def processCSV(self, csvFile):
        self.termList = []
        with open(csvFile, encoding='utf-8') as f:
            data = f.read()
            for line in data.split('\n'):
                for word in line.split(','):
                    if word:
                        self.termList.append(word.lstrip())
        print(self.termList)
        self.list.addItems(self.termList)

    def enableProcessBtn(self):
        if self.xmlDir == None or self.csvInFile == None:
            self.processBtn.setEnabled(False)
            self.progress.setVisible(False)
        else:
            self.processBtn.setEnabled(True)

    def resource_path(self, relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath('.'), relative_path)

    def processXMLDir(self):
        self.progress.setVisible(True)
        with open('output.csv', 'w', encoding='utf-8') as csvfile:
            self.outputData = csv.writer(csvfile, delimiter=',')
            self.outputData.writerow(["FILE", "WORD", "LINE NUMBER", "LINE TEXT"])
            for file in os.listdir(self.xmlDir):
                if ".xml" in file:
                    self.counter[file] = {}
                    for word in self.termList:
                        # print(word)
                        self.counter[file][word] = 0
                        filePath = os.path.join(self.xmlDir, file)
                        with open(filePath, encoding='utf-8') as f:
                            data = f.read()
                            for i, line in enumerate(data.split('\n')):
                                if word.lower() in line.lower():
                                    self.counter[file][word] += 1
                                    print("file: " + file + "\nword: " + word
                                          + "\nline num: " + str(i + 1) + "\n"
                                          + line.lstrip())
                                    self.outputData.writerow([file,
                                                        word,
                                                        i+1,
                                                        line.lstrip()])
                self.progressStatus += 1
                self.progress.setValue(self.progressStatus / len(os.listdir(self.xmlDir)) * 100)
                QApplication.processEvents()
        self.writeOutputFiles()

    def writeOutputFiles(self):
        fileName, _ = QFileDialog.getSaveFileName(self, 'Save File')
        print("FILE NAME", fileName)
        self.makeCountFile(fileName + ".count.csv")
        self.makeOutputFile(fileName + ".output.csv")

    def makeOutputFile(self, fileName):
        os.rename('output.csv', fileName)


    def makeCountFile(self, fileName):
        with open(fileName, 'w') as f:
            f.write("file, " + ', '.join(self.termList))
            f.write('\n')
            for file in self.counter.keys():
                line = file
                for word in self.termList:
                    line += ', '
                    line += str(self.counter[file][word])
                f.write(line + '\n')
        print(self.counter)






app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
