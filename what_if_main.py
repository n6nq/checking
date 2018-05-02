from what_if_auto import Ui_MainWindow

class WhatIfMain(QMainWindow, Ui_MainWindow):
    
    myresize = pyqtSignal('QSize')