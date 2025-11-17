# Импортируем необходимые библиотеки для работы "ПАУКА"
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Инициализация рабочего Браузера с разными Таймаутами
driver = webdriver.Firefox()
driver.set_page_load_timeout(30)
driver.implicitly_wait(10)  # Неявное ожидание элементов
wait = WebDriverWait(driver, 15)  # Явное ожидание

# ЧТО И ГДЕ ПАРСИТ "ПАУК", BASE_URL
url = "https://www.divan.ru/category/likvidatsiya"

try:
    driver.get(url)
    # Ждем загрузки хотя бы одного товара
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product-card"]')))
except TimeoutException:
    print("Страница не загрузилась вовремя")
    driver.quit()
    exit()

# Селекторы на основе структуры сайта divan.ru
products = driver.find_elements(By.CSS_SELECTOR, '[data-testid="product-card"]')

# Создаём список, в который все результаты будем сохранять
parsed_data = []

    # Перебираем товары в своей теме
    for product in products:

    # Ловим ошибки, как только они появляются
    try:
        # Ищем ЭЛЕМЕНТЫ внутри искомой Категории по значению:
        # Наименование товара
        name_element = product.find_element(By.CSS_SELECTOR, '[data-testid="product-title"]')
        name = name_element.text

        # Ссылку находим с помощью атрибута 'href'
        link = name_element.get_attribute('href')

        # Цена
        price_element = product.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]')
        price = price_element.text

        # Размер (пример селектора)
        try:
            size = product.find_element(By.CSS_SELECTOR, '.product-dimensions').text
        except NoSuchElementException:
            size = "Не указан"

        # Цвет (пример селектора)
        try:
            color = product.find_element(By.CSS_SELECTOR, '.product-color').text
        except NoSuchElementException:
            color = "Не указан"

        parsed_data.append([name, price, size, color, link])

    except Exception as e:
        print(f"Ошибка при парсинге товара: {e}")
        # При ошибке пропускает оставшуюся часть итерации и переходит
        # к следующей, парсинг не рухнет
        continue

# Закрываем подключение браузера
driver.quit()

# СОХРАНЕНИЕ в CSV
# Открытие нового файла, задаём ему название и форматирование,
# 'w' означает режим доступа, мы разрешаем вносить данные в таблицу
with open("divanLikvidatsiya.csv", 'w',newline='', encoding='utf-8') as file:

    # Сохранение CSV в отдельный файл и настраиваем запись данных в виде таблицы
    writer = csv.writer(file, delimiter=';')  # Разделитель точка с запятой для лучшей совместимости

    # Создаём первый ряд
    writer.writerow(['Наименование', 'Цена', 'Размер', 'Цвет', 'Ссылка на товар'])

    # Указываем использование списка как источника для рядов таблицы
    writer.writerows(parsed_data)

print(f"Парсинг завершен. Найдено товаров: {len(products)}")
print(f"Парсинг завершен. Сохранено {len(parsed_data)} товаров")