import sqlite3
import sys
import time
from project import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QInputDialog, QMessageBox


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWidget, self).__init__(QMainWindow, Ui_MainWindow)
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        # остальное без изменений
        self.setupUi(self)

        # связываемся с базой данных trainer_db.db
        self.con = sqlite3.connect("data/trainer_db.db")

        self.difficulty_mode = 1  # легкий режим по умолчанию
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
        self.entered_text.textChanged.connect(self.start_timer)

    def showTime(self):  # функция показа значения секундомера
        time_r = int(time.time() - self.start_time)  # разница между началом и текущем временем
        # перевод времени в минуту и секунду
        minutes = time_r // 60
        seconds = time_r % 60
        if minutes > 99:  # если минут больше чем 99, то вывод максимального времени
            self.timer_label.setText('99:99')
        else:
            # создание строки для удобного показа времени
            minutes = str(minutes)
            seconds = str(seconds)
            stopwatch = '0' * (2 - len(minutes)) + minutes + ':' + '0' * (2 - len(seconds)) + seconds
            self.timer_label.setText(stopwatch)

    def start_timer(self):
        if not self.is_start:
            self.is_start = True
            self.start_time = time.time()
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
            con.commit()
        con.close()

    def interface_binding(self):  # функция для привязки интерфейса к функциям
        # настройки темы
        self.dark_theme.triggered.connect(lambda: self.change_theme("dark"))
        self.light_theme.triggered.connect(lambda: self.change_theme("light"))

        # настройки сложности
        self.easy_mode.triggered.connect(lambda: self.change_difficulty(1))
        self.normal_mode.triggered.connect(lambda: self.change_difficulty(2))
        self.hard_mode.triggered.connect(lambda: self.change_difficulty(3))
        self.insane_mode.triggered.connect(lambda: self.change_difficulty(4))

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
        self.difficulty_mode = diff

    def registration(self):
        username, ok_pressed = QInputDialog.getText(self, "Регистрация", "Введите имя пользователя: ")
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
            con = sqlite3.connect("data/trainer_db.db")
            cur = con.cursor()
            cur.execute(f"INSERT INTO Users(nickname) VALUES('{username}')")
            con.commit()
            self.users_id[username] = int(cur.execute(f"""
            SELECT user_id FROM Users
                WHERE nickname = '{username}'""").fetchall()[0][0])
            print(self.users_id)
            con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
