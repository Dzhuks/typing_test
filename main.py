import sqlite3
import sys
import time
from random import choice
from project import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from PyQt5 import QtCore, QtWidgets

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


# Наследуемся от виджета из PyQt5.QtWidgets и от класса с интерфейсом
class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        # остальное без изменений
        self.setupUi(self)

        # связываемся с базой данных trainer_db.db
        self.con = sqlite3.connect("data\\trainer_db.db")

        self.difficulty_mode = 'easy'  # легкий режим по умолчанию
        self.users_id = {}
        self.load_users()
        self.user = "Гость"  # пользователь по умолчанию

        self.theme = "dark"  # тема по умолчанию
        self.interface_binding()

        self.is_start = False  # переменная для отслеживания начало печати пользователя

        # Создание таймера для секундомера
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        self.start_time = 0  # время начало ввода
        self.timeInterval = 100  # интервал вызова

        # привязка и загрузка текстов
        self.entered_text.textChanged.connect(self.compare_texts)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.load_text(self.difficulty_mode)

    def showTime(self):  # функция показа значения секундомера
        time_r = int(time.time() - self.start_time)  # разница между началом и текущем временем
        # перевод времени в минуту и секунду
        minutes = time_r // 60
        seconds = time_r % 60
        if minutes > 59:  # если минут больше чем 59, то вывод максимального времени
            self.timer_label.setText('59:59')
        else:
            # создание строки для удобного показа времени
            minutes = str(minutes)
            seconds = str(seconds)
            stopwatch = '0' * (2 - len(minutes)) + minutes + ':' + '0' * (2 - len(seconds)) + seconds
            self.timer_label.setText(stopwatch)

    def compare_texts(self):
        if not self.is_start:
            self.is_start = True
            self.start_timer()
        else:
            pass

    def start_timer(self):
        self.start_time = time.time()
        self.timer_label.setText('00:00')
        self.timer.start(self.timeInterval)

    def load_users(self):  # загрузка пользователей из базы данных в словарь
        cur = self.con.cursor()
        users = cur.execute("""SELECT user_id, nickname FROM Users""").fetchall()
        for user in users:
            self.users_id[user[1]] = user[0]
            print(user)
        if len(users) == 0:
            cur.execute("INSERT INTO Users(nickname) VALUES('Гость')")
            self.users_id["Гость"] = 1
            self.con.commit()

    def interface_binding(self):  # функция для привязки интерфейса к функциям
        # настройки темы
        self.dark_theme.triggered.connect(lambda: self.change_theme("dark"))
        self.light_theme.triggered.connect(lambda: self.change_theme("light"))

        # настройки сложности
        self.easy_mode.triggered.connect(lambda: self.change_difficulty('easy'))
        self.normal_mode.triggered.connect(lambda: self.change_difficulty('normal'))
        self.hard_mode.triggered.connect(lambda: self.change_difficulty('hard'))
        self.insane_mode.triggered.connect(lambda: self.change_difficulty('insane'))

        # настройки пользователя
        self.register_user.triggered.connect(self.registration)

    def change_theme(self, theme):
        if theme == "light" and theme != self.theme:
            self.theme = "light"
            self.setStyleSheet("color: black")
            self.generated_text.setStyleSheet("color: rgb(14, 70, 255);")
            self.entered_text.setStyleSheet("color: rgb(73, 220, 0);")
            self.hint_label.setStyleSheet("color: rgb(122, 122, 122);")
            self.timer_label.setStyleSheet("color: rgb(14, 70, 255);")
            self.menubar.setStyleSheet("color: black;")
        if theme == "dark" and theme != self.theme:
            self.theme = "dark"
            self.setStyleSheet("background-color: rgb(56, 56, 56); color: white;")
            self.generated_text.setStyleSheet("color: rgb(240, 223, 28);")
            self.entered_text.setStyleSheet("color: rgb(73, 220, 0);")
            self.hint_label.setStyleSheet("color: rgb(161, 161, 161);")
            self.timer_label.setStyleSheet("color: rgb(240, 223, 28);")
            self.menubar.setStyleSheet("color: white;")

    def change_difficulty(self, diff):
        if self.difficulty_mode != diff:
            self.load_text(diff)
        self.difficulty_mode = diff

    def load_text(self, difficult):
        cur = self.con.cursor()
        texts = cur.execute(f"""
        SELECT text FROM Texts 
            WHERE difficulty_id=(
        SELECT difficulty_id FROM Difficults 
            WHERE mode = '{difficult}')
        """).fetchall()
        text = choice(texts)[0]
        while self.generated_text.text() == text:
            text = choice(texts)[0]
        self.generated_text.setText(text)
        self.entered_text.setText("")

    def registration(self):
        username, ok_pressed = QInputDialog.getText(self, "Регистрация", "Введите имя пользователя:")
        if ok_pressed:
            if username in self.users_id:
                error_message = QMessageBox(self)
                error_message.setIcon(QMessageBox.Critical)
                error_message.setText("Пользователь уже существует!")
                error_message.setInformativeText("Введите другое имя пользователя")
                error_message.setWindowTitle("Регистрация отменена")
                error_message.exec_()
                return

            self.user = username
            cur = self.con.cursor()
            cur.execute(f"INSERT INTO Users(nickname) VALUES('{username}')")
            self.con.commit()
            self.users_id[username] = int(cur.execute(f"""
            SELECT user_id FROM Users
                WHERE nickname = '{username}'""").fetchall()[0][0])
            print(self.users_id)

    def closeEvent(self, *args, **kwargs):
        self.con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
