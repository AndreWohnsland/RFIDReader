import sys
import time
import traceback
import string
import RPi.GPIO as GPIO
import MFRC522
import signal

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import *

from ui.mainwindow import Ui_MainWindow
from ui.Keyboard import Ui_Keyboard

class MainScreen(QMainWindow, Ui_MainWindow):
    def __init__(self, devenvironment, parent=None):
        """ Init function for the MainWindow Class. """
        super(MainScreen, self).__init__(parent)
        self.setupUi(self)
        # as long as its not devenvironment (usually touchscreen) hide the cursor
        self.devenvironment = devenvironment
        if not self.devenvironment:
            self.setCursor(Qt.BlankCursor)
        self.scanning = True
        self.this_scan_active = True
        self.threadpool = QThreadPool()

        self.pushButton.clicked.connect(self.write_card)
        self.LE_new_name.clicked.connect(lambda: self.keyboard(self.LE_new_name, max_char_len=16))

        self.scan_thread()

    def write_card(self):
        """Checks the entered name, if valid, tries to write to the card.
        """
        new_name = self.LE_new_name.text()
        # the new name needs to have at least 3 characters
        if len(new_name) <= 2:
            self.dialogbox(
                "Der Name muss mindestens 3 Buchstaben haben.",
                "Name zu kurz"
            )
        # if successfull opens new window with message and tries to scan card
        else:
            text = f"Name ist gültig.\nNeuer Name: {new_name}.\nBitte Karte ans Terminal\nhalten zum überschreiben."
            self.this_scan_active = False
            self.acceptWindow = ScanWindow(self, text, new_name=new_name)
            self.acceptWindow.show()
            self.LE_curr_name.setText("")
            self.LE_new_name.setText("")

    def scan_for_cards(self, progress_callback):
        """Thread function to scan continiously for RFID cards
        
        Args:
            progress_callback (qyptSignal): Signal which pyqt emmits when a progresspoint is reached
        
        Returns:
            bool: Only emmits if the scanning loop was ended
        """
        rfid = MFRC522.MFRC522()
        # Scans continiously for a new card and sleeps shortly
        while self.scanning:
            if self.this_scan_active:
                #print("Mainscanloop...")
                (status, TagType) = rfid.MFRC522_Request(rfid.PICC_REQIDL)
                #if status == rfid.MI_OK:
                #    print("card detected")
                # first gets the status and userid
                (status, uid) = rfid.MFRC522_Anticoll()
                # if its a valid card, get the keys, and tags
                if status == rfid.MI_OK:
                    key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
                    rfid.MFRC522_SelectTag(uid)
                    status = rfid.MFRC522_Auth(rfid.PICC_AUTHENT1A, 8, key, uid)

                    # if everything went right, read out the data from the tag and create the name
                    if status == rfid.MI_OK:
                        data = rfid.MFRC522_Read(8)
                        scanned_name = ("".join(chr(x) for x in data)).strip()
                        rfid.MFRC522_StopCrypto1()
                        progress_callback.emit(scanned_name)
                time.sleep(0.1)
        endstring = True
        return endstring

    def scan_successfull(self, scanned_name):
        """Enters the scanned name from the card.
        
        Args:
            scanned_name (str): Scanned name
        """
        print(f"The read name is: {scanned_name}")
        self.LE_curr_name.setText(scanned_name)

    def scan_ended(self, endstring):
        """Is executed if the worker is has finished.
        
        Args:
            endstring (bool): Returnargument from the worker
        """
        if endstring:
            print("The scan was ended please check program")
        else:
            print("Somehow we got here. Please check the multithreading")

    def scan_thread(self):
        """Thread starter for the worker and the according functions.
        """
        worker = Worker(self.scan_for_cards)
        worker.signals.result.connect(self.scan_ended)
        worker.signals.progress.connect(self.scan_successfull)
        self.threadpool.start(worker)

    def keyboard(self, le_to_write, headertext=None, max_char_len=30):
        """ Opens up the Keyboard to seperate Enter a Name or similar.
        Needs a Lineedit where the text is put in. In addition, the header of the window can be changed. 
        This is only relevant if you dont show the window in Fullscreen!
        """
        self.kbw = KeyboardWidget(self, le_to_write=le_to_write, max_char_len=max_char_len)
        if headertext is not None:
            self.kbw.setWindowTitle(headertext)
        self.kbw.showFullScreen()

    def dialogbox(
        self,
        textstring,
        windowtitle="Message",
        boxtype="standard",
        okstring="OK",
        cancelstring="Cancel",
        parent=None,
    ):
        """The default messagebox for the Maker. Uses a QMessageBox with OK-Button 
        
        Args:
            textstring (str): message displayed on the window
            windowtitle (str, optional): Title of the window. Defaults to "".
            boxtype (str, optional): boxtype, can either be "standard" or "okcancel". Defaults to "standard".
            okstring (str, optional): Text displayed on okay button. Defaults to "OK".
            cancelstring (str, optional): Text displayed on cancle button. Defaults to "Cancel".
            parent (qt_object, optional): Source window for the dialog. Defaults to None.
        
        Returns:
            int: qt specific return value from the dialog
        """
        # print(textstring)
        msgBox = QMessageBox(parent)
        if boxtype == "standard":
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setIcon(QMessageBox.Information)
        elif boxtype == "okcancel":
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            buttoncancel = msgBox.button(QMessageBox.Cancel)
            buttoncancel.setText("{: ^12}".format(cancelstring))
            msgBox.setIcon(QMessageBox.Question)
        buttonok = msgBox.button(QMessageBox.Ok)
        buttonok.setText("{: ^12}".format(okstring))
        msgBox.setText(textstring)
        msgBox.setWindowTitle(windowtitle)
        # msgBox.setWindowIcon(QIcon("gui/pictures/dollar.png"))
        msgBox.show()
        retval = msgBox.exec_()
        if boxtype == "okcancel":
            return retval


class KeyboardWidget(QDialog, Ui_Keyboard):
    """ Creates a Keyboard where the user can enter names or similar strings to Lineedits. """
    def __init__(self, parent, le_to_write=None, max_char_len=30):
        super(KeyboardWidget, self).__init__(parent)
        self.setupUi(self)
        self.ms = parent
        self.le_to_write = le_to_write
        self.LName.setText(self.le_to_write.text())
        # populating all the buttons
        self.backButton.clicked.connect(self.backbutton_clicked)
        self.clear.clicked.connect(self.clearbutton_clicked)
        self.enterButton.clicked.connect(self.enterbutton_clicked)
        self.space.clicked.connect(lambda: self.inputbutton_clicked(" ", " "))
        self.delButton.clicked.connect(self.delete_clicked)
        self.shift.clicked.connect(self.shift_clicked)
        # generating the lists to populate all remaining buttons via iteration
        self.number_list = [x for x in range(10)]
        self.char_list_lower = [x for x in string.ascii_lowercase]
        self.char_list_upper = [x for x in string.ascii_uppercase]
        self.attribute_chars = [getattr(self, "Button" + x) for x in self.char_list_lower]
        self.attribute_numbers = [getattr(self, "Button" + str(x)) for x in self.number_list]
        for obj, char, char2 in zip(self.attribute_chars, self.char_list_lower, self.char_list_upper):
            obj.clicked.connect(lambda _, iv=char, iv_s=char2: self.inputbutton_clicked(inputvalue=iv, inputvalue_shift=iv_s))
        for obj, char, char2 in zip(self.attribute_numbers, self.number_list, self.number_list):
            obj.clicked.connect(lambda _, iv=char, iv_s=char2: self.inputbutton_clicked(inputvalue=iv, inputvalue_shift=iv_s))
        # restricting the Lineedit to a set up Char leng
        self.LName.setMaxLength(max_char_len)

    def backbutton_clicked(self):
        """ Closes the Window without any further action. """
        self.close()
    
    def clearbutton_clicked(self):
        """ Clears the input. """
        self.LName.setText("")

    def enterbutton_clicked(self):
        """ Closes and enters the String value back to the Lineedit. """
        self.le_to_write.setText(self.LName.text())
        self.close()

    def inputbutton_clicked(self, inputvalue, inputvalue_shift):
        """ Enters the inputvalue into the field, adds it to the string.
        Can either have the normal or the shift value, if there is no difference both imput arguments are the same.
        """
        stringvalue = self.LName.text()
        if self.shift.isChecked():
            addvalue = inputvalue_shift
        else:
            addvalue = inputvalue
        stringvalue += str(addvalue)
        self.LName.setText(stringvalue)

    def delete_clicked(self):
        stringvalue = self.LName.text()
        if len(stringvalue) > 0:
            self.LName.setText(stringvalue[:-1])

    def shift_clicked(self):
        if self.shift.isChecked():
            charchoose = self.char_list_upper
        else:
            charchoose = self.char_list_lower
        for obj, char in zip(self.attribute_chars, charchoose):
            obj.setText(str(char))


class ScanWindow(QDialog):

    def __init__(self, parent, LE_name="Something went wrong", new_name=None, app_width=800, app_height=480):
        super(ScanWindow, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(app_width, app_height)
        self.new_name = new_name
        self.data_name = [ord(x) for x in list(new_name)]
        self.ms = parent
        self.backbutton = QPushButton("Abbrechen")
        self.backbutton.setMinimumSize(QSize(0, 150))
        font = QFont()
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        self.backbutton.setFont(font)
        self.backbutton.clicked.connect(lambda: self.cancel_me())

        self.label = QLabel(LE_name)
        self.label.setFont(font)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.backbutton)
        self.setLayout(layout)

        self.scanloop = True
        self.threadpool = QThreadPool()
        self.run_thread()

        if not self.ms.devenvironment:
            self.showFullScreen()

    def run_thread(self):
        worker = Worker(self.cont_scan)
        worker.signals.result.connect(self.result_scan)
        self.threadpool.start(worker)

    def cont_scan(self, progress_callback):
        rfid = MFRC522.MFRC522()
        while self.scanloop:
            #print("in second worker!")
            # first gets the status and userid
            (status, TagType) = rfid.MFRC522_Request(rfid.PICC_REQIDL)
            (status, uid) = rfid.MFRC522_Anticoll()
            # if its a valid card, get the keys, and tags
            if status == rfid.MI_OK:
                key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
                rfid.MFRC522_SelectTag(uid)
                status = rfid.MFRC522_Auth(rfid.PICC_AUTHENT1A, 8, key, uid)

                # if everything went right, read out the data from the tag and create the name
                if status == rfid.MI_OK:
                    for i in range(0,16):
                        self.data_name.append(0x20)
                    rfid.MFRC522_Write(8, self.data_name)
                    rfid.MFRC522_StopCrypto1()
                    self.scanloop = False
                    self.ms.this_scan_active = True
                    self.close()
                    return True
            time.sleep(0.1)
        print("Scanloop interrupted!")
        return None

    def result_scan(self, result):
        if result is not None:
            print("Successfully wrote new card value")

    def cancel_me(self):
        self.scanloop = False
        self.ms.this_scan_active = True
        self.close()


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data
    
    error
        `tuple` (exctype, value, traceback.format_exc() )
    
    result
        `object` data returned from processing, anything

    progress
        `str` indicating scanned name

    """

    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(str)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs["progress_callback"] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
