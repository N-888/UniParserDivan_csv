# Импортируем необходимые библиотеки для работы "ПАУКА"
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By

# Инициализация рабочего Браузера
driver = webdriver.Firefox()

# ЧТО И ГДЕ ПАРСИТ "ПАУК", BASE_URL
url = "https://www.divan.ru/category/likvidatsiya"

# Открываем веб-страницу с Ожиданием (5)с., чтобы успела загрузиться
driver.get(url)
time.sleep(5)

# Находим все карточки с товарами / услугами с помощью названия класса
# Названия классов берём с кода сайта
likvidatsiyas = driver.find_elements(By.CSS_SELECTOR, '__variable_1e6e6e')

# Создаём список, в который все результаты будем сохранять
parsed_data = []

# Перебираем товары в своей искомой теме
for likvidatsiya in likvidatsiyas:

    # Ловим ошибки, как только они появляются
    try:

        # Ищем элементы внутри искомой Категории по значению
        # Наименования
        name_element = likvidatsiya.find_element(By.CSS_SELECTOR, 'a.<deepl-inline>')
        name = name_element.text

        # Находим ссылку с помощью атрибута 'href'
        link = name_element.get_attribute('href')

        # Находим цены товаров
        price = likvidatsiya.find_element(By.CSS_SELECTOR, 'span[data-qa="vacancy-serp__vacancy-employer-text"]').text

        try:

            # Находим размеры товаров
            size = likvidatsiya.find_element(By.CSS_SELECTOR, 'span.compensation-labels--cR9OD8ZegWd3f7Mzxe6z').text
        except:
            size = "Не указана"

        try:

            # Находим цвета товаров
            color = likvidatsiya.find_element(By.CSS_SELECTOR, 'span.compensation-labels--cR9OD8ZegWd3f7Mzxe6z').text
        except:
            color = "Не указана"

    except Exception as e:
        print(f"Произошла ошибка при парсинге: {e}")

        # При ошибке пропускает оставшуюся часть итерации и переходит
        # к следующей, парсинг не рухнет
        continue

    # Вносим найденную информацию в список
    parsed_data.append([name, price, size, color, url])

# Закрываем подключение браузера
driver.quit()

# Прописываем открытие нового файла, задаём ему название и форматирование
# 'w' означает режим доступа, мы разрешаем вносить данные в таблицу
with open("divanLikvidatsiya.csv", 'w',newline='', encoding='utf-8') as file:

    # Используем модуль csv и настраиваем запись данных в виде таблицы
    # Сам объект
    writer = csv.writer(file)

    # Создаём первый ряд
    writer.writerow(['Наименование', 'цена', 'размеры', 'цвет', 'ссылка на товар'])

    # Прописываем использование списка как источника для рядов таблицы
    writer.writerows(parsed_data)
