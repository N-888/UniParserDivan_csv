# Импортируем необходимые библиотеки для работы "ПАУКА"
import requests  # Для отправки HTTP-запросов к сайту
from bs4 import BeautifulSoup  # Для парсинга HTML-страницы
import csv  # Для работы с CSV-файлами
import re  # Для работы с регулярными выражениями

# Настраиваем заголовки браузера, чтобы сайт не блокировал наши запросы
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

# Указываем URL-адрес СТРАНИЦЫ, которую будем ПАРСИТЬ
url = "https://www.divan.ru/category/likvidatsiya"

# Выводим сообщение о начале загрузки страницы
print("Загружаем страницу...")

# Обрабатываем возможные ошибки при загрузке страницы
try:
    # Отправляем GET-запрос на сайт с таймаутом 30 секунд
    response = requests.get(url, headers=headers, timeout=30)
    # Устанавливаем правильную кодировку для русского текста
    response.encoding = 'utf-8'
    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Сообщаем об успешной загрузке
    print("Страница успешно загружена!")

except Exception as e:
    # В случае ошибки выводим сообщение и завершаем программу
    print(f"Ошибка при загрузке страницы: {e}")
    exit()

# Ищем все карточки товаров на странице по специальному атрибуту data-testid
products = soup.find_all('div', {'data-testid': 'product-card'})
# Выводим количество найденных товаров для отладки
print(f"Найдено товаров: {len(products)}")

# Создаём список, в который будем сохранять все результаты парсинга
parsed_data = []

# Перебираем каждый товар в цикле для извлечения информации
for i, product in enumerate(products):
    # Защита от сбоев - обрабатываем каждый товар в отдельном блоке try-except
    try:
        # НАИМЕНОВАНИЕ ТОВАРА: ищем элемент с названием товара
        name = "Не указано"  # Значение по умолчанию
        name_element = product.find('div', class_='Name_name__Wqn5R')
        if name_element:
            name = name_element.get_text(strip=True)  # Извлекаем текст и убираем лишние пробелы

        # ССЫЛКА НА ТОВАР: находим ссылку на страницу товара
        link = "Не указано"  # Значение по умолчанию
        link_element = product.find('link', itemprop='url')
        if link_element and link_element.get('href'):
            # Формируем полную ссылку, добавляя домен
            link = 'https://www.divan.ru' + link_element['href']

        # ЦЕНА ТОВАРА: извлекаем актуальную цену
        price = "Не указана"  # Значение по умолчанию
        price_element = product.find('span', class_='FullPrice_actual__Mio07')
        if price_element:
            price_text = price_element.get_text(strip=True)
            # Очищаем цену от лишних символов, оставляя только цифры и пробелы
            price = re.sub(r'[^\d\s]', '', price_text).strip()

        # РАЗМЕР ТОВАРА: ищем размеры в характеристиках
        size = "Не указан"  # Значение по умолчанию
        characteristics = product.find('ul', class_='CharacteristicsList_wrapper__kTKMv')
        if characteristics:
            size_items = []  # Список для хранения найденных размеров
            # Перебираем все характеристики товара
            for char in characteristics.find_all('li', class_='CharacteristicsList_characteristics__hoycR'):
                title = char.find('span', class_='CharacteristicsList_title__1haLD')
                value = char.find_all('span')[-1]  # Берем последний span с значением
                if title and value:
                    title_text = title.get_text(strip=True)
                    value_text = value.get_text(strip=True)
                    # Проверяем, относится ли характеристика к размерам
                    if any(word in title_text.lower() for word in ['размер', 'габарит', 'место']):
                        size_items.append(f"{title_text}: {value_text}")

            # Если нашли размеры, объединяем их в строку
            if size_items:
                size = '; '.join(size_items)

        # ЦВЕТ ТОВАРА: определяем цвет из названия товара
        color = "Не указан"  # Значение по умолчанию
        # Список ключевых слов для поиска цвета в названии
        color_keywords = ['белый', 'черный', 'серый', 'коричневый', 'бежевый',
                          'синий', 'зеленый', 'красный', 'желтый', 'оранжевый',
                          'фиолетовый', 'розовый', 'голубой']
        # Ищем цвет в названии товара
        for keyword in color_keywords:
            if keyword in name.lower():
                color = keyword.capitalize()  # Делаем первую букву заглавной
                break

        # СТАРАЯ ЦЕНА: находим оригинальную цену до скидки
        old_price = "Не указана"  # Значение по умолчанию
        old_price_element = product.find('span', class_='FullPrice_expired__BjSFe')
        if old_price_element:
            old_price_text = old_price_element.get_text(strip=True)
            # Очищаем старую цену от лишних символов
            old_price = re.sub(r'[^\d\s]', '', old_price_text).strip()

        # СКИДКА: извлекаем процент скидки
        discount = "0"  # Значение по умолчанию
        discount_element = product.find('div', class_='DiscountAndTag_discount__sMc_8')
        if discount_element:
            discount = discount_element.get_text(strip=True).replace('%', '')

        # НАЛИЧИЕ ТОВАРА: проверяем наличие товара на складе
        availability = "Не указано"  # Значение по умолчанию
        availability_tag = product.find('div', class_='Tags_tag__RA7ds')
        if availability_tag:
            availability = availability_tag.get_text(strip=True)

        # Добавляем найденную информацию в список, если есть название товара
        if name != "Не указано":
            parsed_data.append([name, price, size, color, discount, old_price, availability, link])
            # Выводим информацию об успешно обработанном товаре
            print(f"Успешно {i + 1}: {name} - {price} руб. (-{discount}%)")

    except Exception as e:
        # В случае ошибки выводим сообщение и продолжаем парсинг остальных товаров
        print(f"Ошибка при парсинге товара {i + 1}: {e}")
        continue

# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ В CSV-ФАЙЛ
if parsed_data:
    # Открываем файл для записи с правильной кодировкой
    with open("divanLikvidatsiya.csv", 'w', newline='', encoding='utf-8') as file:
        # Создаем объект для записи CSV с разделителем точка с запятой
        writer = csv.writer(file, delimiter=';')
        # Записываем заголовки столбцов таблицы
        writer.writerow(
            ['Наименование', 'Цена', 'Размер', 'Цвет', 'Скидка%', 'Старая цена', 'Наличие', 'Ссылка на товар'])
        # Записываем все данные из списка в файл
        writer.writerows(parsed_data)
    # Выводим итоговое сообщение об успешном сохранении
    print(f"\nПарсинг завершен! Сохранено {len(parsed_data)} товаров в файл divanLikvidatsiya.csv")
else:
    # Сообщаем, если не удалось спарсить ни одного товара
    print("\nНе удалось спарсить ни одного товара.")

# ВЫВОД СТАТИСТИКИ ПАРСИНГА для анализа результатов
if parsed_data:
    print("\n=== СТАТИСТИКА ПАРСИНГА ===")
    print(f"Всего обработано товаров: {len(parsed_data)}")

    # Анализ товаров с ценами
    priced_items = [item for item in parsed_data if item[1] != "Не указана"]
    if priced_items:
        # Сортируем товары по цене (от высокой к низкой)
        priced_items.sort(key=lambda x: int(x[1].replace(' ', '')) if x[1].replace(' ', '').isdigit() else 0,
                          reverse=True)
        print("\nТОП-5 самых дорогих товаров:")
        for i, item in enumerate(priced_items[:5]):
            print(f"  {i + 1}. {item[0]} - {item[1]} руб.")

    # Анализ товаров со скидками
    discounted_items = [item for item in parsed_data if item[4] != "0"]
    if discounted_items:
        # Сортируем товары по размеру скидки (от большой к маленькой)
        discounted_items.sort(key=lambda x: int(x[4]) if x[4].isdigit() else 0, reverse=True)
        print("\nТОП-5 товаров с наибольшими скидками:")
        for i, item in enumerate(discounted_items[:5]):
            print(f"  {i + 1}. {item[0]} - {item[1]} руб. (-{item[4]}%)")

    # Подсчет товаров в наличии
    available_items = [item for item in parsed_data if "в наличии" in item[6].lower()]
    print(f"\nТоваров в наличии: {len(available_items)} из {len(parsed_data)}")