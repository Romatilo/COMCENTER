import requests
import json
from dotenv import load_dotenv
import os

# Загрузка переменных из .env файла
load_dotenv()

# Получение API-ключа и ID поисковой системы из .env
api_key = os.getenv("GOOGLE_API_KEY")
cx = os.getenv("GOOGLE_CSE_ID")

# Переменная города (можно менять)
city = "Кемерово"

# Запрос для поиска полиграфических услуг в указанном городе
query = f"полиграфические услуги типография {city} site:*.ru | site:*.com -inurl:(форум | блог)"

# Основная логика
def main():
    if not api_key or not cx:
        print("Ошибка: Не удалось загрузить GOOGLE_API_KEY или GOOGLE_CSE_ID из .env файла.")
        return

    # Параметры запроса к Google API
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": query,
        "num": 10,  # Количество результатов на страницу (максимум 10)
        "start": 1
    }

    # Список для хранения сайтов
    websites = []
    failed_requests = []

    # Парсинг Google API
    for start in range(1, 101, 10):  # До 100 результатов
        params["start"] = start
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            for item in data.get("items", []):
                website = item["link"]
                websites.append(website)
                print(f"Найден сайт: {website}")
        except requests.RequestException as e:
            print(f"Ошибка Google API на странице {start}: {e}")
            failed_requests.append(f"Страница {start}: {str(e)}")
            break

    # Удаление дубликатов
    websites = list(dict.fromkeys(websites))

    # Имя файла с учетом города
    output_file = f"websites_{city}.txt"

    # Сохранение сайтов в .txt файл
    with open(output_file, "w", encoding='utf-8') as f:
        for website in websites:
            f.write(f"{website}\n")
    print(f"Сайты сохранены в '{output_file}' (всего: {len(websites)})")

    # Сохранение ошибок (если были) в отдельный файл
    if failed_requests:
        with open(f"failed_requests_{city}.txt", "w", encoding='utf-8') as f:
            for error in failed_requests:
                f.write(f"{error}\n")
        print(f"Ошибки сохранены в 'failed_requests_{city}.txt'")

if __name__ == "__main__":
    main()