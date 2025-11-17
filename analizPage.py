import requests
from bs4 import BeautifulSoup
import csv

# Настройки для запросов
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

url = "https://www.divan.ru/category/likvidatsiya"

try:
    response = requests.get(url, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.content, 'html.parser')

    print("Анализируем структуру страницы...")

    # Ищем все карточки товаров
    product_cards = soup.find_all('div', {'data-product-id': True})
    print(f"Найдено карточек товаров по data-product-id: {len(product_cards)}")

    # Если не нашли, ищем другими способами
    if not product_cards:
        product_cards = soup.select('[class*="product"], [class*="card"]')
        print(f"Найдено карточек по классам: {len(product_cards)}")

    # Выводим структуру первых 2 карточек для анализа
    for i, card in enumerate(product_cards[:2]):
        print(f"\n=== Карточка товара {i + 1} ===")
        print("HTML структура:")
        print(card.prettify()[:1000])  # Первые 1000 символов

        # Пробуем извлечь данные
        name = card.find(['h3', 'div', 'a'],
                         class_=lambda x: x and any(word in x for word in ['name', 'title', 'product']))
        if name:
            print(f"Название: {name.get_text(strip=True)}")

        price = card.find(class_=lambda x: x and any(word in x for word in ['price', 'cost', 'value']))
        if price:
            print(f"Цена: {price.get_text(strip=True)}")

        link = card.find('a', href=True)
        if link:
            print(f"Ссылка: {link['href']}")

        print("=" * 50)

    # Сохраняем полный HTML для ручного анализа
    with open("full_analysis.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print("\nПолный HTML сохранен в full_analysis.html")

except Exception as e:
    print(f"Ошибка: {e}")