# подключения к необходимым библиотекам
import sqlite3
import sys
import time
import csv
import datetime
from random import choice, randint
from project import Ui_MainWindow
from res_dialog import Ui_Dialog
from recordings_window import Ui_Form
from PyQt5.QtWidgets import QDialog, QInputDialog, QMessageBox
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QTextCursor, QPixmap

# адаптация к экранам с высоким разрешением (HiRes)
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


# константы
DATABASE = "data\\trainer_db.db"
GREEN = '#49DC01'
RED = '#DC143C'


# конвертирование sql запроса в csv файл
def convert_sql_to_csv(name, data):  # в функцию передаем имя файла и данные
    # ключи csv файла
    titles = [description[0] for description in cur.description]

    with open(name, 'w+', newline='') as csv_file:  # открываем файл, если он есть, а иначе создаем его
        writer = csv.DictWriter(
            csv_file, fieldnames=titles,
            delimiter=';', quoting=csv.QUOTE_NONNUMERIC)  # объект для записи (writer)
        writer.writeheader()  # пишем заголовок titles
        # запись в csv файл
        for d in data:
            writer.writerow({titles[i]: d[i] for i in range(len(titles))})


# конвертирование sql запроса в csv файл
def convert_sql_to_txt(name, data):  # в функцию передаем имя файла и данные

    with open(name, 'w+') as txt_file:  # открываем файл, если он есть, а иначе создаем его
        for elem in data:
            txt_file.write(elem[0])
            txt_file.write('\n')


def create_item(text, flags):
    table_widget_item = QTableWidgetItem(text)
    table_widget_item.setFlags(flags)
    return table_widget_item


class RecordingsWindow(QWidget, Ui_Form):
    def __init__(self, user):
        super().__init__()  # конструктор родительского класса
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        self.setupUi(self)
        self.username_labe.setText(user)
        self.load_table(user)

    def load_table(self, user):

        keys = ['record_id', 'user_id', 'data', 'text_id', 'difficulty_id', 'time', 'typing_speed']

        con = sqlite3.connect(DATABASE)

        # Создание курсора
        cur = con.cursor()

        result = cur.execute(f"""
        SELECT {', '.join(keys)} FROM Recordings
            WHERE user_id=(
        SELECT user_id FROM Users WHERE nickname='{user}')
        """).fetchall()

        self.recordings_table.setColumnCount(len(keys))
        self.recordings_table.setHorizontalHeaderLabels(keys)
        self.recordings_table.setRowCount(len(result))

        for i, row in enumerate(result):
            for j, col in enumerate(row):
                if keys[j] == 'user_id':
                    col = user
                elif keys[j] == 'text_id':
                    que = f"""
                    SELECT text FROM Texts
                        WHERE text_id={col}"""

                    col = cur.execute(que).fetchall()[0][0]

                elif keys[j] == 'difficult_id':
                    que = f"""
                    SELECT mode FROM Difficults
                        WHERE difficulty_id={col}"""

                    col = cur.execute(que).fetchall()[0][0]

                self.recordings_table.setItem(i, j, create_item(str(col), Qt.ItemIsEnabled))


# Наследуемся от виджета из PyQt5.QtWidgets и от класса с интерфейсом
class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        self.setupUi(self)

        # связываемся с базой данных trainer_db.db
        self.con = sqlite3.connect(DATABASE)

        self.difficulty_mode = 'easy'  # легкий режим по умолчанию
        self.users_id = {}
        self.load_users()
        self.user = "Гость"  # пользователь по умолчанию

        self.theme = "dark"  # тема по умолчанию
        self.interface_binding()  # привязка частей интерфейса к функциям

        self.is_program_change = False  # переменная для отслеживания изменения программой текста
        self.is_stopwatch_start = False  # переменная для отслеживания начало старта секундомера

        # Создание секундомера
        self.stopwatch = QTimer(self)
        self.stopwatch.timeout.connect(self.show_stopwatch)
        self.start_time = 0  # время начало ввода
        self.timeInterval = 100  # интервал вызова секундомера
        self.time_r = 0  # разница между начальным временем и текущем временем. Изначально равен 0

        self.load_text(self.difficulty_mode)
        # при изменении текста в entered_text вызвать функцию text_changed
        self.entered_text.textChanged.connect(self.text_changed)

    # обработчик событий нажатия клавиш и мыши
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # при нажатие на esc начать заново
            self.start_again()

    # начать заново ввод текста
    def start_again(self):
        self.is_program_change = True  # программа изменила текст
        self.reset_stopwatch()  # перезапустить секундомер
        self.entered_text.setText("")  # обнулить вводимый текст
        self.is_program_change = False  # вернуться к исходному значению

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
        if not self.is_program_change:
            if not self.is_stopwatch_start:  # если таймер был не запущен, запустить его
                self.start_stopwatch()
            self.compare_texts()

    # функция сравнения текстов из generated_text и entered_text
    def compare_texts(self):
        cursor = self.entered_text.textCursor()
        generated_text = self.generated_text.text()
        entered_text = self.entered_text.toPlainText()
        is_correct = True
        html = ""
        for index, character in enumerate(entered_text):
            if index <= len(generated_text) - 1:
                if generated_text[index] != character:
                    is_correct = False
            else:
                is_correct = False
            color = GREEN if is_correct else RED
            html += f"<font color='{color}' size = {4} >{character}</font>"
        self.is_program_change = True
        self.entered_text.setHtml(html)
        self.is_program_change = False
        self.entered_text.setTextCursor(cursor)
        if is_correct and len(entered_text) == len(generated_text):
            self.show_and_load_recording()

    def show_and_load_recording(self):
        # Создание курсора
        cur = self.con.cursor()

        # Получение user_id путем запроса из таблицы Users
        user_id = cur.execute(f"""
            SELECT user_id FROM Users 
                WHERE nickname='{self.user}'""").fetchall()[0][0]

        # Получение текущей даты при помощи библиотеки datetime
        data = datetime.datetime.now().date()

        # Получение text_id путем запроса из таблицы Texts
        text_id = cur.execute(f"""
            SELECT text_id FROM Texts
                WHERE text='{self.generated_text.text()}'""").fetchall()[0][0]

        # Получение difficulty_id путем запроса из таблицы Texts
        difficulty_id = cur.execute(f"""
            SELECT difficulty_id FROM Difficults
                WHERE mode='{self.difficulty_mode}'""").fetchall()[0][0]

        # Получение time через self.stopwatch_label.text()
        time = self.stopwatch_label.text()

        # typing_speed = S / time * 60 сим/мин
        typing_speed = len(self.generated_text.text()) / self.time_r * 60

        # добавляем запись в бд и показываем результат пользователю
        self.load_recording(user_id, data, text_id, difficulty_id, time, typing_speed)
        self.show_result(time, typing_speed)

    def load_recording(self, user_id, data, text_id, difficulty_id, time, typing_speed):
        # Создание курсора
        cur = self.con.cursor()

        que = f"""INSERT INTO Recordings(user_id, data, text_id, difficulty_id, time, typing_speed) 
        VALUES ({user_id}, {data}, {text_id}, {difficulty_id}, '{time}', {typing_speed})"""

        cur.execute(que)

        self.con.commit()

    # функция показа результата пользователя
    def show_result(self, time, typing_speed):
        self.stopwatch.stop()  # остановка секундомера
        dialog = ResultsDialog(time, typing_speed)
        dialog.show()
        dialog.exec()

    # запуск секундомера
    def start_stopwatch(self):
        self.is_stopwatch_start = True
        self.start_time = time.time()  # в качестве начального времени установить текущее время
        self.time_r = 0  # Обнулить разницу во времени
        self.stopwatch_label.setText('00:00')
        self.stopwatch.start(self.timeInterval)  # запуск секундомера с итервалом timeInterval

    # сброс секундомера
    def reset_stopwatch(self):
        self.is_stopwatch_start = False
        self.start_time = 0  # в качестве начального времени установить 0
        self.time_r = 0  # Обнулить разницу во времени
        self.stopwatch_label.setText('00:00')
        self.stopwatch.stop()  # остановка секундомера

    # функция показа значения секундомера
    def show_stopwatch(self):
        # обновить разницу во времени
        self.time_r = int(time.time() - self.start_time)

        # перевод времени в минуту и секунду
        minutes = self.time_r // 60
        seconds = self.time_r % 60
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

    # функция для входа в пользователя
    def login(self):
        # получение ника для входа
        username, ok_pressed = QInputDialog.getItem(self, "Вход", "Выберите пользователя: ",
                                                    self.users_id.keys(), 1, False)
        # если пользователь нажал на ОК, то сменить пользователя
        if ok_pressed:
            self.user = username  # смена пользователя

    # функция, которая вызывается, когда закрывается окно
    def closeEvent(self, *args, **kwargs):
        # Закрытие соединение с базой данных при закрытие окна
        self.con.close()


class ResultsDialog(QDialog, Ui_Dialog):
    def __init__(self, time, result):
        super().__init__()  # конструктор родительского класса
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        self.setupUi(self)
        self.button_box.accepted.connect(self.accept_data)  # привязка функции кнопки ОК

        self.time_label.setText(f"Общее время: {time}")
        self.cpm_label.setText(f"Символов в минуту: {result:.{1}f}")
        # num = randint(1, 5)  # получение рандомного номера картинки
        # pixmap = QPixmap(f"data\\image_{num}")  # получение картинки из data
        # self.image_label.setPixmap(pixmap)  # вставка картинки в label

    # функция для закрытия окна на нажатие ОК
    def accept_data(self):
        self.close()


if __name__ == '__main__':
    # Создание класса приложения PyQT
    app = QApplication(sys.argv)
    # создание экземпляра класса MyWidget
    ex = MyWidget()
    # показ экземпляра
    ex.show()

    recordings_window = RecordingsWindow('Гость')

    recordings_window.show()
    # при завершение исполнения QApplication завершить программу
    sys.exit(app.exec())
