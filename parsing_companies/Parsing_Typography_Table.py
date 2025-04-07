import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

# Заголовки для имитации браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Регулярные выражения для телефона и email
phone_pattern = re.compile(r'(\+?\d[\d\s()-]{8,}\d)')
email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

# Чтение списка сайтов из файла websites.txt
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
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Попытка исправить кодировку
        try:
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)
        except UnicodeDecodeError:
            soup = BeautifulSoup(response.content.decode('utf-8', errors='replace'), 'html.parser')

        # 1. Наименование компании
        company_name = soup.title.text.strip() if soup.title else "Не найдено"
        if not company_name or company_name == "Не найдено":
            h1 = soup.find('h1')
            company_name = h1.text.strip() if h1 else "Не найдено"
        company_name = ''.join(c if ord(c) < 128 or c.isprintable() else ' ' for c in company_name)

        # 2. Адрес сайта
        website = url

        # 3. Все номера телефонов
        phones = []
        for text in soup.stripped_strings:
            try:
                phone_matches = phone_pattern.findall(text)
                for match in phone_matches:
                    if match not in phones:  # Убираем дубликаты
                        phones.append(match.strip())
            except UnicodeDecodeError:
                continue
        phone_str = ", ".join(phones) if phones else "Не найдено"

        # 4. Email
        email = "Не найдено"
        for text in soup.stripped_strings:
            try:
                email_match = email_pattern.search(text)
                if email_match:
                    email = email_match.group()
                    break
            except UnicodeDecodeError:
                continue

        # 5. Печатные машины
        printing_machines = "Не найдено"
        machine_keywords = ['печатная машина', 'принтер', 'оборудование', 'press', 'printer', 'machine']
        for text in soup.stripped_strings:
            try:
                if any(keyword.lower() in text.lower() for keyword in machine_keywords):
                    printing_machines = text.strip()
                    break
            except UnicodeDecodeError:
                continue

        return {
            "Наименование Компании": company_name,
            "Адрес сайта": website,
            "Номер телефона": phone_str,
            "Email": email,
            "Печатные машины": printing_machines
        }

    except (requests.RequestException, Exception) as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return None

# Основная логика
def main():
    # Путь к файлу со списком сайтов
    file_path = "websites.txt"

    # Загружаем список сайтов
    websites = load_websites(file_path)
    if not websites:
        print("Список сайтов пуст или файл 'websites.txt' не найден.")
        return

    # Списки для данных
    websites_data = []
    failed_websites = []

    # Парсинг каждого сайта
    for website in websites:
        print(f"Обрабатываю: {website}")
        result = parse_website(website)
        if result:
            websites_data.append(result)
        else:
            failed_websites.append({"website": website})

    # Сохранение успешных данных в XLSX
    df = pd.DataFrame(websites_data)
    output_file = "printing_companies.xlsx"
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f"Успешные данные сохранены в '{output_file}'")

    # Сохранение проблемных сайтов в JSON
    with open("failed_websites.json", "w", encoding='utf-8') as f:
        json.dump(failed_websites, f, ensure_ascii=False, indent=4)
    print("Проблемные сайты сохранены в 'failed_websites.json'")

if __name__ == "__main__":
    main()