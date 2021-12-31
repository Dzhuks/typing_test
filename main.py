# подключения к необходимым библиотекам
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
# адаптация к экранам с высоким разрешением (HiRes)
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


# Наследуемся от виджета из PyQt5.QtWidgets и от класса с интерфейсом
class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        self.setupUi(self)

        # связываемся с базой данных trainer_db.db
        self.con = sqlite3.connect("data\\trainer_db.db")

        self.difficulty_mode = 'easy'  # легкий режим по умолчанию
        self.users_id = {}
        self.load_users()
        self.user = "Гость"  # пользователь по умолчанию

        self.theme = "dark"  # тема по умолчанию
        self.interface_binding()  # привязка частей интерфейса к функциям

        self.is_programme_change = False  # переменная для отслеживания изменения программой текста
        self.is_stopwatch_start = False  # переменная для отслеживания начало старта секундомера

        # Создание секундомера
        self.stopwatch = QTimer(self)
        self.stopwatch.timeout.connect(self.show_stopwatch)
        self.start_time = 0  # время начало ввода
        self.timeInterval = 100  # интервал вызова секундомера

        # при изменении текста в entered_text вызвать функцию text_changed
        self.entered_text.textChanged.connect(self.text_changed)

    # обработчик событий нажатия клавиш и мыши
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # при нажатие на esc начать заново
            self.start_again()

    # начать заново ввод текста
    def start_again(self):
        self.is_programme_change = True  # программа изменила текст
        self.reset_stopwatch()  # перезапустить секундомер
        self.entered_text.setText("")  # обнулить вводимый текст
        self.is_programme_change = False  # вернуться к исходному значению

    # загрузка нового текста со сложностью difficult из таблицы Texts
    def load_text(self, difficult):
        # Создание курсора
        cur = self.con.cursor()

        # Выполнение запроса и получение всех результатов
        texts = cur.execute(f"""
        SELECT text FROM Texts 
            WHERE difficulty_id=(
        SELECT difficulty_id FROM Difficults 
            WHERE mode = '{difficult}')
        """).fetchall()

        # выбирание случайного текста, пока он совпадает с текстом в generated_text
        text = choice(texts)[0]
        while self.generated_text.text() == text:
            text = choice(texts)[0]
        self.generated_text.setText(text)  # вставить новой текст в generated_text

        # начать заново, так как текст в generated_text изменился
        self.start_again()

    # обработчик события изменения текста
    def text_changed(self):
        if not self.is_programme_change:  # если изменения не сделаны программой, то начать сравнивать тексты
            if not self.is_stopwatch_start:  # если таймер был не запущен, запустить его
                self.start_stopwatch()
            self.compare_texts()

    # функция сравнения текстов из generated_text и entered_text
    def compare_texts(self):  # функция заглушка
        pass

    # запуск секундомера
    def start_stopwatch(self):
        self.is_stopwatch_start = True
        self.start_time = time.time()  # в качестве начального времени установить текущее время
        self.stopwatch_label.setText('00:00')
        self.stopwatch.start(self.timeInterval)  # запуск секундомера с итервалом timeInterval

    # сброс секундомера
    def reset_stopwatch(self):
        self.is_stopwatch_start = False
        self.start_time = 0  # в качестве начального времени установить 0
        self.stopwatch_label.setText('00:00')
        self.stopwatch.stop()  # остановка секундомера

    # функция показа значения секундомера
    def show_stopwatch(self):
        # разница между начальным временем и текущем временем
        time_r = int(time.time() - self.start_time)

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
            self.stopwatch_label.setText(stopwatch)

    # загрузка пользователей из базы данных в словарь
    def load_users(self):
        # Создание курсора
        cur = self.con.cursor()

        # Выполнение запроса и получение всех результатов
        users = cur.execute("""SELECT user_id, nickname FROM Users""").fetchall()

        # если сохраненных пользователей ноль, то пользователь будет Гостем
        if len(users) == 0:
            # добавление в таблицу Users Гостя
            cur.execute("INSERT INTO Users(nickname) VALUES('Гость')")
            # присваение Гостю id 1
            self.users_id["Гость"] = 1
            # зафиксировать изменения в БД
            self.con.commit()
        else:
            # установка к каждому пользователю свой id
            for user in users:
                self.users_id[user[1]] = user[0]
                print(user)

    # функция для привязки частей интерфейса к функциям
    def interface_binding(self):
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

    # функция изменения темы
    def change_theme(self, theme):
        if theme == "light" and theme != self.theme:
            # установка светлой темы
            self.theme = "light"
            self.setStyleSheet("color: black")
            self.generated_text.setStyleSheet("color: rgb(14, 70, 255);")
            self.entered_text.setStyleSheet("color: rgb(73, 220, 0);")
            self.hint_label.setStyleSheet("color: rgb(122, 122, 122);")
            self.stopwatch_label.setStyleSheet("color: rgb(14, 70, 255);")
            self.menubar.setStyleSheet("color: black;")
        elif theme == "dark" and theme != self.theme:
            # установка темной темы
            self.theme = "dark"
            self.setStyleSheet("background-color: rgb(56, 56, 56); color: white;")
            self.generated_text.setStyleSheet("color: rgb(240, 223, 28);")
            self.entered_text.setStyleSheet("color: rgb(73, 220, 0);")
            self.hint_label.setStyleSheet("color: rgb(161, 161, 161);")
            self.stopwatch_label.setStyleSheet("color: rgb(240, 223, 28);")
            self.menubar.setStyleSheet("color: white;")

    # функция изменения сложности
    def change_difficulty(self, diff):
        # если сложность не осталось такой же, то поменять текст в generated_text со сложностью diff
        if self.difficulty_mode != diff:
            self.load_text(diff)
        # изменить сложность
        self.difficulty_mode = diff

    # функция регистраций пользователя
    def registration(self):
        # вызов диалогового окна
        username, ok_pressed = QInputDialog.getText(self, "Регистрация", "Введите имя пользователя:")

        # если пользователь нажал на ОК, то добавить его в таблицу Users в БД
        if ok_pressed:
            # если пользователь уже существует, то вызвать окно с ошибкой
            if username in self.users_id:
                error_message = QMessageBox(self)
                error_message.setIcon(QMessageBox.Critical)
                error_message.setText("Пользователь уже существует!")
                error_message.setInformativeText("Введите другое имя пользователя")
                error_message.setWindowTitle("Регистрация отменена")
                error_message.exec_()
                return

            # поменять пользователя
            self.user = username

            # Создание курсора
            cur = self.con.cursor()

            # добавляем пользователя в таблицу Users из БД
            cur.execute(f"INSERT INTO Users(nickname) VALUES('{username}')")

            # зафиксировать изменения в БД
            self.con.commit()

            # присвоение пользователю username id путем запроса из таблицы Users
            self.users_id[username] = int(cur.execute(f"""
            SELECT user_id FROM Users
                WHERE nickname = '{username}'""").fetchall()[0][0])
            print(self.users_id)

    # функция, которая вызывается, когда закрывается окно
    def closeEvent(self, *args, **kwargs):
        # Закрытие соединение с базой данных при закрытие окна
        self.con.close()


if __name__ == '__main__':
    # Создание класса приложения PyQT
    app = QApplication(sys.argv)
    # создание экземпляра класса MyWidget
    ex = MyWidget()
    # показ экземпляра
    ex.show()
    # при завершение исполнения QApplication завершить программу
    sys.exit(app.exec())
