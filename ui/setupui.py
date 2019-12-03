import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *

from ui.setup_mainwindow import MainScreen


def create_main_window(devenvironment, app_width=800, app_height=480):
    """Creates the instance of the MainWindow
    
    Args:
        devenvironment (bool): Value if you are in the developmentmodus
        app_width (int, optional): Width of the screen. Defaults to 800.
        app_height (int, optional): Height of the screen. Defaults to 480.
    """

    # creates the application
    app = QApplication(sys.argv)
    #creates the mainscreen, sets it to fixed size and fullscreen
    w = MainScreen(devenvironment)
    w.showFullScreen()
    w.setFixedSize(app_width, app_height)
    # runs the app until the exit
    sys.exit(app.exec_())
    # at the end closes the DB
    w.DB.close()