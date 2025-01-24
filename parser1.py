import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


base_path = 'https://www.danceplus.ru/catalog/khudozhestvennaya_gimnastika/'
pagination_suffix = '?PAGEN_2='


option = Options()
option.add_argument("--disable-infobars")

# Инициализация браузера
browser = webdriver.Chrome(options=option)


# собственно, парсер с поиском по элементам с полученной страницы
def get_from_page(path: str):
    """
    :path: адрес страницы, строка
    :returns: список словарей в формате [{name: value, price: value}, ...]
    :rtype: list
    """
    browser.get(path)

    try:
        start_time = time.time()
        items = WebDriverWait(browser, 9).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "item"))
        )
        elapsed_time = time.time() - start_time
        if elapsed_time < 9:
            time.sleep(9 - elapsed_time)  # Дополнительное ожидание

        product_data = []
        for item in items:
            try:
                # поиск title внутри текущего item
                title_element = item.find_element(By.XPATH, ".//a[contains(@class, 'item-link')]/div[contains(@class, 'title')]/span")
                # Уточняем поиск, чтобы исключить title из "Мы в соцсетях"
                #  - выбираем <a> с классом "item-link"
                #  - внутри него ищем <div> с классом "title"
                #  - внутри этого <div> ищем <span>
                price_element = item.find_element(By.CLASS_NAME, "price")
                price_text = price_element.find_element(By.TAG_NAME, 'span').text  # Извлекаем текст из span внутри price
                # почистим цену, иногда попадаются лишние символы, вроде "руб."
                filtered_price = ''.join(filter(lambda x: x.isdigit(), price_text))
                product_data.append({
                    "title": title_element.text,
                    "price": filtered_price
                })
            except Exception as e:
                # отладка
                # print(f"Некоторые данные товара отсутствуют в этом блоке. Ошибка: {e}")
                continue
        return product_data
    except Exception as e:
        print(f"Произошла ошибка: {e}")