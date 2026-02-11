import requests
import json
from datetime import datetime, timedelta
import os
import csv
from tqdm import tqdm
import time
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/cbr_parser.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CBRCurrencyParser:
    """Парсер курсов валют с сайта ЦБ РФ"""
    
    def __init__(self, currency_code='USD'):
        self.base_url = "https://www.cbr-xml-daily.ru/archive/{year}/{month:02d}/{day:02d}/daily_json.js"
        self.currency_code = currency_code
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_date_range(self, start_date, end_date):
        """Генерирует список дат для парсинга"""
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        return dates
    
    def fetch_currency_rate(self, date):
        """Получает курс валюты на конкретную дату"""
        url = self.base_url.format(
            year=date.year,
            month=date.month,
            day=date.day
        )
        
        try:
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if self.currency_code in data['Valute']:
                    rate = data['Valute'][self.currency_code]['Value']
                    nominal = data['Valute'][self.currency_code]['Nominal']
                    name = data['Valute'][self.currency_code]['Name']
                    
                    logger.debug(f"Загружен курс на {date.strftime('%Y-%m-%d')}: {rate}")
                    return {
                        'date': date.strftime('%Y-%m-%d'),
                        'currency': self.currency_code,
                        'name': name,
                        'nominal': nominal,
                        'rate': rate
                    }
            elif response.status_code == 404:
                logger.debug(f"Нет данных за {date.strftime('%Y-%m-%d')}")
            else:
                logger.warning(f"Ошибка {response.status_code} на {date.strftime('%Y-%m-%d')}")
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Ошибка подключения на {date.strftime('%Y-%m-%d')}")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Ошибка на {date.strftime('%Y-%m-%d')}: {e}")
        
        return None
    
    def collect_rates(self, start_date, end_date, delay=0.5):
        """Собирает курсы за период"""
        dates = self.get_date_range(start_date, end_date)
        logger.info(f"Начало сбора данных за {len(dates)} дней")
        logger.info(f"Валюта: {self.currency_code}")
        
        results = []
        for date in tqdm(dates, desc="Сбор курсов"):
            rate_data = self.fetch_currency_rate(date)
            if rate_data:
                results.append(rate_data)
            time.sleep(delay)
            
        logger.info(f"Собрано записей: {len(results)} из {len(dates)}")
        return results
    
    def save_to_csv(self, data, filename='dataset/currency_rates.csv'):
        """Сохраняет данные в CSV"""
        os.makedirs('dataset', exist_ok=True)
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'currency', 'name', 'nominal', 'rate'])
            writer.writeheader()
            writer.writerows(data)
            
        logger.info(f"Данные сохранены в {filename}")
        
def main():
    """Основная функция"""
    print("=" * 60)
    print("ПАРСЕР КУРСОВ ВАЛЮТ ЦБ РФ")
    print("=" * 60)
    print("\nДоступные валюты:")
    print("1. USD - Доллар США")
    print("2. EUR - Евро")
    print("3. CNY - Юань")
    print("4. JPY - Японская йена")
    print("5. KRW - Корейская вона")
    print("6. INR - Индийская рупия")
    print("7. BYN - Белорусский рубль")
    
    choice = input("\nВыберите валюту (1-7): ").strip()
    
    currency_map = {
        '1': 'USD',
        '2': 'EUR', 
        '3': 'CNY',
        '4': 'JPY',
        '5': 'KRW',
        '6': 'INR',
        '7': 'BYN'
    }
    
    currency = currency_map.get(choice, 'USD')
    print(f"\nВыбрана валюта: {currency}")
    
    # Период сбора данных
    print("\nВыберите период:")
    print("1. За 2024 год")
    print("2. За 2023-2024 гг")
    print("3. За всё время (2005-2025)")
    print("4. Свой период")
    
    period = input("Выберите период (1-4): ").strip()
    
    end_date = datetime.now().date()
    
    if period == '1':
        start_date = datetime(2024, 1, 1).date()
    elif period == '2':
        start_date = datetime(2023, 1, 1).date()
    elif period == '3':
        start_date = datetime(2005, 1, 1).date()
    else:
        year = int(input("Введите год начала (например, 2020): "))
        start_date = datetime(year, 1, 1).date()
    
    print(f"\nПериод сбора: {start_date} - {end_date}")
    
    # Создаем парсер
    parser = CBRCurrencyParser(currency_code=currency)
    
    # Собираем данные
    data = parser.collect_rates(start_date, end_date, delay=0.3)
    
    if data:
        # Сохраняем
        filename = f'dataset/{currency}_rates_{start_date.year}_{end_date.year}.csv'
        parser.save_to_csv(data, filename)
        
        print(f"\n✅ Сбор завершен!")
        print(f"📊 Всего записей: {len(data)}")
        print(f"💾 Файл: {filename}")
        
        # Показываем первые 5 записей
        print("\n📋 Первые 5 записей:")
        print("-" * 50)
        print(f"{'Дата':<12} {'Курс':<10} {'Валюта'}")
        print("-" * 50)
        for rate in data[:5]:
            print(f"{rate['date']:<12} {rate['rate']:<10.4f} {rate['currency']}")
    else:
        print("❌ Данные не собраны")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()