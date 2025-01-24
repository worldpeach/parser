from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  # только в парсере 2


base_path = 'https://green-spark.ru/catalog/komplektuyushchie_dlya_remonta/zapchasti_dlya_mobilnykh_ustroystv/displei_2/?set_filter=y&arrFilter_P13_MIN&arrFilter_P13_MAX&onlyAvailable=true'
pagination_suffix = '&page='


option = Options()
option.add_argument("--disable-infobars")
option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

# Инициализация браузера
browser = webdriver.Chrome(options=option)


# the parser
def get_from_page(path: str):
    browser.get(path)
    try:
        # Ждем появления карточек (до 10 секунд)
        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-card"))
        )
        # получаем фактическое состояние html 
        page_source = browser.execute_script("return document.documentElement.outerHTML")
        # отладка
        #print(page_source)
        #with open("debug.html", "w", encoding="utf-8") as f:
        #    f.write(page_source)
        soup = BeautifulSoup(page_source.encode('utf-8'), 'html.parser')
        # Ищем все карточки товаров по уникальному классу
        product_cards = soup.find_all('div', class_='card product-card')
        # отладка
        #print('all the product_cards', product_cards)
        product_data = []
        for card in product_cards:
            try:
                name_elem = card.find('div', class_='product-card-name')
                price_elem = card.find('div', class_='price-value')
                # отладка
                # print(name_elem, price_elem)
                if name_elem and price_elem:
                    name = name_elem.get_text(strip=True)
                    price = price_elem.get_text(strip=True)
                    # почистим цену
                    filtered_price = ''.join(filter(lambda x: x.isdigit(), price))
                    # отладка
                    # print(name, filtered_price)
                    product_data.append({'title': name, 'price': filtered_price})
            except Exception as inner_e:
                print(f"Ошибка при извлечении данных из карточки: {inner_e}")
        return product_data
    except Exception as e:
        print(f"Произошла ошибка при загрузке страницы: {e}")
        print(f"по адресу: {path}")
