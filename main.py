# подключения к необходимым библиотекам
import sqlite3
import sys
import time
from random import choice, randint
from project import Ui_MainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QDialog, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from PyQt5 import QtCore, QtWidgets
import csv
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QPixmap
from res_dialog import Ui_Dialog


# адаптация к экранам с высоким разрешением (HiRes)
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


# константы
DATABASE = "data\\trainer_db.db"
GRAY1 = "#383838"
GRAY2 = "#7a7a7a"
GREEN = "#49dc00"
YELLOW = "#f0df1c"
BLUE = "#0e46ff"
RED = "#DC143C"

OCEAN_GREEN = "#6fffeb"
OCEAN_BLUE = "#304cff"
OCEAN_RED = "#f3633f"
OCEAN_YELLOW = "#ffcb52"

PURPLE = "#1b0051"

PASTEL_BLUE = "#b5ebf3"
PASTEL_PURPLE = "#4343ca"
PASTEL_GREEN = "#a0e546"
PASTEL_RED = "#ff8091"

GLAMOUR_PINK = "#ff7ef4"
GLAMOUR_GRAY = "#787878"
GLAMOUR_BLUE = "#32f7f0"
GLAMOUR_RED = "#ff0000"

FOREST_GREEN = "#6caa33"
FOREST_BROWN = "#81593e"
FOREST_LIGHT_GREEN = "#ebffb4"
FOREST_RED = "#d03739"

# конвертирование sql запроса в csv файл
def convert_sql_to_csv(name, request):  # в функцию передаем имя файла и сам запрос
    # связываемся с базой данных trainer_db.db
    con = sqlite3.connect(DATABASE)

    # Создание курсора
    cur = con.cursor()

    # Выполнение запроса и получение всех результатов
    data = cur.execute(request).fetchall()

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
def convert_sql_to_txt(name, request):  # в функцию передаем имя файла и сам запрос
    # связываемся с базой данных trainer_db.db
    con = sqlite3.connect(DATABASE)

    # Создание курсора
    cur = con.cursor()

    # Выполнение запроса и получение всех результатов
    data = cur.execute(request).fetchall()

    with open(name, 'w+') as txt_file:  # открываем файл, если он есть, а иначе создаем его
        for elem in data:
            txt_file.write(elem[0])


# Наследуемся от виджета из PyQt5.QtWidgets и от класса с интерфейсом
class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        self.setupUi(self)

        # связываемся с базой данных trainer_db.db
        self.con = sqlite3.connect(DATABASE)

        self.difficulty_mode = 'easy'  # легкий режим по умолчанию
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

        # при изменении текста в entered_text вызвать функцию text_changed
        self.entered_text.textChanged.connect(self.text_changed)
        # цвет для выделения правильного текста
        self.correct_color = "#49dc00"
        #
        self.incorrect_color = "#DC143C"

        self.load_text(self.difficulty_mode)

    # обработчик событий нажатия клавиш и мыши
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:  # при нажатие на esc начать заново
            self.load_text(self.difficulty_mode)

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
        green = self.correct_color
        red = self.incorrect_color
        html = ""
        for index, character in enumerate(entered_text):
            if index <= len(generated_text) - 1:
                if generated_text[index] != character:
                    is_correct = False
            else:
                is_correct = False
            color = green if is_correct else red
            html += f"<font color='{color}' size = {4} >{character}</font>"
        self.is_program_change = True
        self.entered_text.setHtml(html)
        self.is_program_change = False
        self.entered_text.setTextCursor(cursor)
        if is_correct and len(entered_text) == len(generated_text):
            self.show_result()

    # функция показа результата пользователя
    def show_result(self):
        dialog = ResultsDialog("1:30", 250, self.theme)
        print("Loten before show")
        dialog.show()
        dialog.exec()
        print("Koten total")
        self.load_text(self.difficulty_mode)

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
            # зафиксировать изменения в БД
            self.con.commit()

    # функция для привязки частей интерфейса к функциям
    def interface_binding(self):
        # настройки темы
        self.dark_theme.triggered.connect(self.set_dark_theme)
        self.light_theme.triggered.connect(self.set_light_theme)
        self.ocean_theme.triggered.connect(self.set_ocean_theme)
        self.violet_theme.triggered.connect(self.set_violet_theme)
        self.pastel_theme.triggered.connect(self.set_pastel_theme)
        self.forest_theme.triggered.connect(self.set_forest_theme)
        self.glamour_theme.triggered.connect(self.set_glamour_theme)

        # настройки сложности
        self.easy_mode.triggered.connect(lambda: self.change_difficulty('easy'))
        self.normal_mode.triggered.connect(lambda: self.change_difficulty('normal'))
        self.hard_mode.triggered.connect(lambda: self.change_difficulty('hard'))
        self.insane_mode.triggered.connect(lambda: self.change_difficulty('insane'))

        # настройки пользователя
        self.register_user.triggered.connect(self.registration)
        self.login_user.triggered.connect(self.login)

    # функция установки светлой темы
    def set_light_theme(self):
        # если светлая тема еще не установлена
        if self.theme != "light":
            self.theme = "light"
            self.correct_color = GREEN
            self.incorrect_color = RED
            self.setStyleSheet("color: black")
            self.generated_text.setStyleSheet(f"color: {BLUE};")
            self.entered_text.setStyleSheet(f"color: {GREEN};")
            self.hint_label.setStyleSheet(f"color: {GRAY2};")
            self.stopwatch_label.setStyleSheet(f"color: {BLUE};")
            self.username_label.setStyleSheet(f"color: {BLUE}")
            self.menubar.setStyleSheet("color: black;")

    # функция установки темной темы
    def set_dark_theme(self):
        # если темная тема еще не установлена
        if self.theme != "dark":
            self.theme = "dark"
            self.correct_color = GREEN
            self.incorrect_color = RED
            self.setStyleSheet(f"background-color: {GRAY1}; color: white;")
            self.generated_text.setStyleSheet(f"color: {YELLOW};")
            self.entered_text.setStyleSheet(f"color: {GREEN};")
            self.hint_label.setStyleSheet(f"color: {GRAY2};")
            self.stopwatch_label.setStyleSheet(f"color: {YELLOW};")
            self.username_label.setStyleSheet(f"color: {YELLOW  }")
            self.menubar.setStyleSheet("color: white;")

    # функция установки океанной темы
    def set_ocean_theme(self):
        # если океанная тема еще не установлена
        if self.theme != "ocean":
            self.theme = "ocean"
            self.correct_color = OCEAN_GREEN
            self.incorrect_color = OCEAN_RED
            self.setStyleSheet(f"background-color: {OCEAN_BLUE}; color: white;")
            self.generated_text.setStyleSheet(f"color: {OCEAN_YELLOW};")
            self.entered_text.setStyleSheet(f"color: {OCEAN_GREEN};")
            self.hint_label.setStyleSheet(f"color: {GRAY2};")
            self.stopwatch_label.setStyleSheet(f"color: {OCEAN_YELLOW};")
            self.username_label.setStyleSheet(f"color: {OCEAN_YELLOW}")
            self.menubar.setStyleSheet("color: white;")

    # функция установки сиреневой темы
    def set_pastel_theme(self):
        # если сиреневая тема еще не установлена
        if self.theme != "pastel":
            self.theme = "pastel"
            self.correct_color = PASTEL_GREEN
            self.incorrect_color = PASTEL_RED
            self.setStyleSheet(f"background-color: {PASTEL_PURPLE}; color: white;")
            self.generated_text.setStyleSheet(f"color: {PASTEL_BLUE};")
            self.entered_text.setStyleSheet(f"color: {PASTEL_GREEN};")
            self.hint_label.setStyleSheet(f"color: {GRAY2};")
            self.stopwatch_label.setStyleSheet(f"color: {PASTEL_BLUE};")
            self.username_label.setStyleSheet(f"color: {PASTEL_BLUE}")
            self.menubar.setStyleSheet("color: white;")

    # функция установки фиолетовой темы
    def set_violet_theme(self):
        # если фиолетовая тема еще не установлена
        if self.theme != "violet":
            self.theme = "violet"
            self.correct_color = GREEN
            self.incorrect_color = RED
            self.setStyleSheet(f"background-color: {PURPLE}; color: white;")
            self.generated_text.setStyleSheet(f"color: {YELLOW};")
            self.entered_text.setStyleSheet(f"color: {GREEN};")
            self.hint_label.setStyleSheet(f"color: {GRAY2};")
            self.stopwatch_label.setStyleSheet(f"color: {YELLOW};")
            self.username_label.setStyleSheet(f"color: {YELLOW  }")
            self.menubar.setStyleSheet("color: white;")

    # функция установки лесной темы
    def set_forest_theme(self):
        # если лесная тема еще не установлена
        if self.theme != "forest":
            self.theme = "forest"
            self.correct_color = FOREST_LIGHT_GREEN
            self.incorrect_color = FOREST_RED
            self.setStyleSheet(f"background-color: {FOREST_GREEN}; color: white;")
            self.generated_text.setStyleSheet(f"color: {FOREST_BROWN};")
            self.entered_text.setStyleSheet(f"color: {FOREST_LIGHT_GREEN};")
            self.hint_label.setStyleSheet(f"color: {GRAY2};")
            self.stopwatch_label.setStyleSheet(f"color: {FOREST_BROWN};")
            self.username_label.setStyleSheet(f"color: {FOREST_BROWN}")
            self.menubar.setStyleSheet("color: white;")

    # функция установки гламурной темы
    def set_glamour_theme(self):
        # если гламурная тема еще не установлена
        if self.theme != "glamour":
            self.theme = "glamour"
            self.setStyleSheet(f"background-color: {GLAMOUR_PINK}; color: white;")
            self.generated_text.setStyleSheet(f"color: white;")
            self.entered_text.setStyleSheet(f"color: {GLAMOUR_BLUE};")
            self.hint_label.setStyleSheet(f"color: {GLAMOUR_GRAY};")
            self.stopwatch_label.setStyleSheet(f"color: white;")
            self.username_label.setStyleSheet(f"color: white")
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
            cur = self.con.cursor()
            users = cur.execute("""SELECT nickname FROM Users""")
            if username in users:
                error_message = QMessageBox(self)
                error_message.setIcon(QMessageBox.Critical)
                error_message.setText("Пользователь уже существует!")
                error_message.setInformativeText("Введите другое имя пользователя")
                error_message.setWindowTitle("Регистрация отменена")
                error_message.exec_()
                return

            # поменять пользователя
            self.user = username
            # изменить ник отображаемый в окне
            self.username_label.setText(username)

            # Создание курсора
            cur = self.con.cursor()

            # добавляем пользователя в таблицу Users из БД
            cur.execute(f"INSERT INTO Users(nickname) VALUES('{username}')")

            # зафиксировать изменения в БД
            self.con.commit()

    # функция для входа в пользователя
    def login(self):
        cur = self.con.cursor()
        # получение списка ников всех пользователей
        users = cur.execute("SELECT nickname FROM Users").fetchall()
        users = map(lambda x: x[0], users)
        # получение ника для входа
        username, ok_pressed = QInputDialog.getItem(self, "Вход", "Выберите пользователя: ",
                                                    users, 0, False)
        # если пользователь нажал на ОК, то сменить пользователя
        if ok_pressed:
            self.user = username  # смена пользователя
            # изменить ник отображаемый в окне
            self.username_label.setText(username)

    # функция, которая вызывается, когда закрывается окно
    def closeEvent(self, *args, **kwargs):
        # Закрытие соединение с базой данных при закрытие окна
        self.con.close()


class ResultsDialog(QDialog, Ui_Dialog):
    def __init__(self, time, result, theme):
        QDialog.__init__(self)  # конструктор родительского класса
        # Вызываем метод для загрузки интерфейса из класса Ui_Dialog,
        self.setupUi(self)
        # изменение темы на тему основного окна
        self.change_theme(theme)
        self.button_box.accepted.connect(self.accept_data)  # привязка функции кнопки ОК

        self.time_label.setText(f"Общее время: {time}")
        self.cpm_label.setText(f"Символов в минуту: {result}")
        # if result < 100:
        #     img = "image1.jpg"
        # elif 100 <= result < 170:
        #     img = "image2.jpg"
        # elif 170 <= result < 250:
        #     img = "image3.jpg"
        # elif 250 <= result <= 350:
        #     img = "image4.jpg"
        # else:
        #     img = "image5.jpg"
        # # try:
        # #     pixmap = QPixmap(img)
        # # except Exception:
        # #     raise FileNotFoundError("Файлы с изображениями не найдены")
        # pixmap = QPixmap(img)
        # self.image_label.setPixmap(pixmap)  # вставка картинки в label

    # функция для закрытия окна на нажатие ОК
    def accept_data(self):
        self.close()

    def change_theme(self, theme):
        print("Koten")
        if theme == "dark":
            self.setStyleSheet(f"background-color: {GRAY1}; color: {YELLOW}")
        elif theme == "light":
            self.setStyleSheet(f"background-color: white; color: {BLUE}")
        elif theme == "ocean":
            self.setStyleSheet(f"background-color: {OCEAN_BLUE}; color: {OCEAN_YELLOW}")
        elif theme == "pastel":
            print("Koten2")
            self.setStyleSheet(f"background-color: white; color: {PASTEL_BLUE}")
            print("Koten3")
        elif theme == "violet":
            self.setStyleSheet(f"background-color: {PURPLE}; color: {YELLOW}")
        elif theme == "forest":
            self.setStyleSheet(f"background-color: {FOREST_GREEN}; color: {FOREST_BROWN}")
        elif theme == "glamour":
            self.setStyleSheet(f"background-color: {GLAMOUR_PINK}; color: white")


if __name__ == '__main__':
    # Создание класса приложения PyQT
    app = QApplication(sys.argv)
    # создание экземпляра класса MyWidget
    ex = MyWidget()
    # показ экземпляра
    ex.show()
    # при завершение исполнения QApplication завершить программу
    sys.exit(app.exec())
