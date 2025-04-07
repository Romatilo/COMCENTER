import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Заголовки для имитации браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Регулярные выражения для поиска телефона и email
phone_pattern = re.compile(r'(\+?\d[\d\s()-]{8,}\d)')
email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Чтение списка сайтов из текстового файла
def load_websites(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            websites = [line.strip() for line in file if line.strip()]
        return websites
    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        return []

# Функция парсинга сайта
def parse_website(url):
    try:
        # Получаем содержимое сайта с обработкой кодировки
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Проверяем кодировку и исправляем, если она некорректна
        if response.encoding == 'ISO-8859-1' or 'charset' not in response.text:
            response.encoding = 'utf-8'  # Предполагаем UTF-8, если кодировка не указана корректно
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Наименование компании (ищем в теге title или h1)
        company_name = soup.title.text.strip() if soup.title else "Не найдено"
        if not company_name or company_name == "Не найдено":
            h1 = soup.find('h1')
            company_name = h1.text.strip() if h1 else "Не найдено"

        # 2. Адрес сайта
        website = url

        # 3. Поиск номера телефона
        phone = "Не найдено"
        for text in soup.stripped_strings:
            phone_match = phone_pattern.search(text)
            if phone_match:
                phone = phone_match.group()
                break

        # 4. Поиск email
        email = "Не найдено"
        for text in soup.stripped_strings:
            email_match = email_pattern.search(text)
            if email_match:
                email = email_match.group()
                break

        # 5. Поиск информации о печатных машинах (по ключевым словам)
        printing_machines = "Не найдено"
        machine_keywords = ['печатная машина', 'принтер', 'оборудование', 'press', 'printer', 'machine']
        for text in soup.stripped_strings:
            if any(keyword.lower() in text.lower() for keyword in machine_keywords):
                printing_machines = text.strip()
                break

        return {
            "Наименование Компании": company_name,
            "Адрес сайта": website,
            "Номер телефона": phone,
            "Email": email,
            "Печатные машины": printing_machines
        }

    except requests.RequestException as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None  # Возвращаем None, чтобы отметить ошибку

# Сохранение списка сайтов с ошибками
def save_failed_websites(failed_sites):
    with open("failed_websites.txt", "w", encoding='utf-8') as file:
        for site in failed_sites:
            file.write(f"{site}\n")
    print(f"Сайты с ошибками сохранены в 'failed_websites.txt'")

# Основная логика
def main():
    # Путь к текстовому файлу со списком сайтов
    file_path = "websites.txt"
    
    # Загружаем список сайтов
    websites = load_websites(file_path)
    if not websites:
        print("Список сайтов пуст или файл не найден. Создайте файл 'websites.txt' с URL.")
        return

    # Список для хранения данных и сайтов с ошибками
    data = []
    failed_websites = []

    # Парсинг каждого сайта
    for site in websites:
        print(f"Обрабатываю: {site}")
        result = parse_website(site)
        if result is not None:
            data.append(result)
        else:
            failed_websites.append(site)

    # Создание таблицы с помощью pandas
    df = pd.DataFrame(data)

    # Сохранение в XLSX
    output_file = "printing_companies.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Данные сохранены в файл '{output_file}'")

    # Сохранение сайтов с ошибками
    if failed_websites:
        save_failed_websites(failed_websites)
    else:
        print("Ошибок при парсинге не было.")

if __name__ == "__main__":
    main()