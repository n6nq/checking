#imports
import sys
import os
# get the Qt files
import PyQt5
from PyQt5.QtWidgets import *
import database

# get the window
import mainwindow_auto
from checkfiledialog import CheckFileDialog
import readcheckfile_auto

# create class for Raspberry Pi GUI
########################################################################
class MainWindow(QMainWindow, mainwindow_auto.Ui_MainWindow):
    """"""

    # access variables inside the UI's file
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        
        self.btnOn.clicked.connect(lambda: self.pressedOnButton())
        self.btnReadFile.clicked.connect(lambda: self.pressedReadCheckFileButton())
        
        curr = os.getcwd()
        self.db = database.Database(curr+'\\checking')
#       self.db.open(curr+'\\checking')
#        self.db.createAccount('checking')
        
    def pressedOnButton(self):
        print ("Pressed On!")
        for i in range(1, 11):
            self.listCategorized.addItem("Number %d" % i)
        
    def pressedReadCheckFileButton(self):
        print ("Pressed Off!")
        for i in range(5):
            self.listUnCategorized.addItem("Numero %d" % i)
        
        readIt = CheckFileDialog(self.db)
        print(readIt.cf)
        
        
def main():
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    
        
        
        
    
    