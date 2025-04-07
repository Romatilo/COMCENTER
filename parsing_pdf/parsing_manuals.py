import requests
from bs4 import BeautifulSoup
import os
import time

# URL сайта
base_url = "https://www.km-shop.ru"
start_url = "https://www.km-shop.ru/konica-minolta/?s=pop"  # Обновлённый URL для принтеров

# Заголовки для имитации браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Папка для сохранения файлов
download_folder = "zip_catalogs"
if not os.path.exists(download_folder):
    os.makedirs(download_folder)

def download_file(url, filename):
    """Скачивает файл по URL и сохраняет его локально"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(os.path.join(download_folder, filename), 'wb') as f:
            f.write(response.content)
        print(f"Скачан файл: {filename}")
    except requests.RequestException as e:
        print(f"Ошибка при скачивании {url}: {e}")

def parse_page(url):
    """Парсит страницу и ищет ссылки на PDF-файлы с 'ЗИП каталог'"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем все ссылки на странице
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Проверяем, является ли ссылка ссылкой на PDF
            if href.endswith('.pdf'):
                # Проверяем, содержит ли название "ЗИП каталог"
                if "ЗИП каталог" in link.text:
                    pdf_url = href if href.startswith('http') else base_url + href
                    filename = href.split('/')[-1]
                    download_file(pdf_url, filename)
            # Если ссылка ведет на другую страницу сайта, парсим её рекурсивно
            elif href.startswith('/') or base_url in href:
                next_url = href if href.startswith('http') else base_url + href
                if "printer" in next_url.lower() and next_url not in visited:
                    visited.add(next_url)
                    time.sleep(1)  # Задержка в 1 секунду между запросами
                    parse_page(next_url)

    except requests.RequestException as e:
        print(f"Ошибка при загрузке страницы {url}: {e}")

# Множество для отслеживания посещённых страниц
visited = set([start_url])

# Запускаем парсинг
print(f"Начинаем парсинг с {start_url}")
parse_page(start_url)
print("Парсинг завершён")