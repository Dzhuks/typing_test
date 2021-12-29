import sqlite3
import sys
import time
from project import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.con = sqlite3.connect("data/trainer_db.db")
        self.is_start = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.start_time = 0
        self.timeInterval = 100
        self.entered_text.textChanged.connect(self.start_timer)

    def showTime(self):
        time_r = int(time.time() - self.start_time)
        minutes = time_r // 60
        seconds = time_r % 60
        if minutes > 99:
            self.timer_label.setText('99:99')
        else:
            minutes = str(minutes)
            seconds = str(seconds)
            stopwatch = '0' * (2 - len(minutes)) + minutes + ':' + '0' * (2 - len(seconds)) + seconds
            self.timer_label.setText(stopwatch)

    def start_timer(self):
        if not self.is_start:
            self.is_start = True
            self.start_time = time.time()
            self.timer.start(self.timeInterval)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())