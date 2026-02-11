from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("=" * 60)
print("ТЕСТОВЫЙ ПАРСЕР ПОГОДЫ GISMETEO (CHROME)")
print("=" * 60)

# Настройка Chrome
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')  # Новый режим headless
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

print("\n[1] Запуск Chrome...")
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("✅ Браузер запущен")
    
    url = "https://www.gismeteo.ru/diary/4368/2025/1/"
    print(f"[2] Загрузка страницы: {url}")
    driver.get(url)
    
    # Ждем загрузку
    time.sleep(5)
    
    print("[3] Поиск данных...")
    
    # Пробуем разные варианты поиска таблицы
    selectors = [
        "table.wdata",
        "table.archive",
        "table[class*='weather']",
        "table"
    ]
    
    table = None
    for selector in selectors:
        try:
            table = driver.find_element(By.CSS_SELECTOR, selector)
            if table:
                print(f"✅ Таблица найдена по селектору: {selector}")
                break
        except:
            continue
    
    if table:
        rows = table.find_elements(By.TAG_NAME, "tr")
        print(f"Строк в таблице: {len(rows)}")
        
        if len(rows) > 1:
            print(f"\n{'День':<8} {'Температура':<15} {'Давление':<12} {'Ветер':<15}")
            print("-" * 70)
            
            for row in rows[1:11]:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 6:
                    day = cols[0].text.strip()
                    temp = cols[1].text.strip()
                    pressure = cols[3].text.strip()
                    wind = cols[4].text.strip()
                    print(f"{day:<8} {temp:<15} {pressure:<12} {wind:<15}")
    else:
        print("❌ Таблица не найдена")
        
        # Сохраняем страницу для анализа
        with open('gismeteo_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("✅ Страница сохранена в gismeteo_page.html")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("\n💡 Советы:")
    print("1. Проверьте, установлен ли Chrome")
    print("2. Попробуйте переустановить webdriver-manager: pip install --upgrade webdriver-manager")
    print("3. Если не работает - перейдем на парсинг ЦБ РФ")

finally:
    try:
        driver.quit()
    except:
        pass

print("\n" + "=" * 60)
input("Нажмите Enter для выхода...")