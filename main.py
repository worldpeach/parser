"""
usage examples
# python3 main.py -p parser1 -o db1 -f csv
# python3 main.py -p parser1 -o db1 -f xls
# python3 main.py --parser parser2 --output pars2_250_a_z_xls --format xls --sort desc
"""
import parser1
import parser2
import csv
import xlwt  # pip install xlwt
from statistics import median  # https://sky.pro/wiki/python/raschyot-mediany-spiska-v-python-uchtite-dublikaty-i-razmer/
import argparse  # cli


NUM_POSITIONS_TO_PARSE = 250


def save_to_xls(data: list, filename: str):
    """
    Сохраняет список словарей в XLS файл.
    
    :param data: Список словарей, содержащих 'title' и 'price'.
    :param filename: Имя файла для сохранения (без расширения .xls).
    """
    # Проверка на пустой список
    if not data:
        print('Нечего записывать в XLS. Получен пустой список.')
        return None

    # Создаем новую книгу Excel
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Sheet 1')

    # Заголовки столбцов
    headers = ['id', 'title', 'price']
    for col_num, header in enumerate(headers):
        sheet.write(0, col_num, header)

    # Заполняем данными
    for row, item in enumerate(data, start=1):
        sheet.write(row, 0, row)  # id
        sheet.write(row, 1, item['title'])
        sheet.write(row, 2, item['price'])

    # Сохраняем файл
    try:
        workbook.save(f"{filename}")
        print(f"Данные успешно сохранены в {filename}")
    except Exception as e:
        print(f"Произошла ошибка при сохранении файла: {e}")


def save_to_csv(data: list, filename: str):
    """
    Сохраняет список словарей в CSV файл.
    
    :param data: Список словарей, содержащих 'title' и 'price'.
    :param filename: Имя файла для сохранения.
    """

    # прервём выполнение, если подан пустой список
    if not data:
        print('Нечего записывать в CSV. Получен пустой список.')
        return None

    # тут можно добавить логику инициализации файла, проверки, что он непустой, переименования файла, чтобы избежать перезаписи.

    # newline='' гарантирует, что обработка переносов будет кроссплатформенной.
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        # отладка
        # print(f'filename {filename}')
        # Определяем заголовки столбцов
        fields = ['id', 'title', 'price']
        writer = csv.DictWriter(file, fieldnames=fields)

        # записывает строку заголовков в CSV-файл
        # мы использовали writer(), который у нас заменил стандартные методы writeline() и writelines()
        writer.writeheader()  

        # и данные, добавляя порядковый номер
        for index, item in enumerate(data, start=1):
            row = {'id': index, 'title': item['title'], 'price': item['price']}
            writer.writerow(row)


def save(data: list, filename: str, file_format: str):
    # Выберем функцию для сохранения, в зависимости от формата
    if file_format == "csv":
        save_to_csv(data, filename + "." + file_format)
    elif file_format == "xls":
        save_to_xls(data, filename + "." + file_format)


def create_page_generator(base, suffix):  # в lambda?
    for page_number in range(1, 30):
        yield base + suffix + str(page_number)


def calculate_mediana(product_list):
    """
    Функция для конкретной структуры из списка словарей, в котором значение с ключом 'price' будет ценой
    """

    # обработает как с цену с копейками, так и без
    numbers = list(map(lambda x: float(x['price']), product_list))

    return median(numbers)


def sort_products(prods: list, order: str):
    """
    Сортирует данные по имени продукта.
    :prods: Несортированный список словарей, одним из ключей которого является "title"
    :order: Порядок сортировки. 
                  "asc" (от "ascending") для сортировки по возрастанию, 
                  "desc" (от "descending") для сортировки по убыванию.
    """

    return sorted(prods, key=lambda x: x["title"], reverse=order == "desc")


# функция только для отладки
def print_report(parsed_products, gotten_from="не указано"):
    """
    Принимает список и выдаёт исключение, если он пустой.
    """
    if not parsed_products:
        raise Exception('Что-то не так с парсингом страницы, получен пустой результат')
    
    #print(f'Результаты со страницы {gotten_from}')

    for i in range(1, len(parsed_products)):
        print(f"{i}. {parsed_products[i]['title']} - {parsed_products[i]['price']} руб.")


def process_data(args):
    """Функция обработки данных с заданными параметрами."""
    print(f"Запуск парсера {args.parser}, сохранение как {args.output}.{args.format}, сортировка: {('z-a', 'a-z')[args.sort == 'asc']}")
     
    # определимся с используемым парсером
    if args.parser == 'parser1':
        parser = parser1
    elif args.parser == 'parser2':
        parser = parser2

    page_generator = create_page_generator(parser.base_path, parser.pagination_suffix)

    parsed_products = []  # главный список, где будут все результаты сбора

    # пока словарь не достигнет нужного количества собранных позиций
    while len(parsed_products) < NUM_POSITIONS_TO_PARSE:
        updated_path = next(page_generator)

        # отладка
        print(f'Открываю {updated_path}')
        page_result = parser.get_from_page(updated_path)
        #print_report(page_result, updated_path)

        # если всё ок, расширим главный список результатов
        parsed_products.extend(page_result)


    # отладка
    # print('итоговый общий несортированный список')
    # print_report(parsed_products, updated_path)

    # затем отсортировать
    sorted_products = sort_products(parsed_products, args.sort)

    # только для отладки
    #print('итоговый общий сортированный список')
    #print_report(sorted_products, updated_path)


    # сохранить результаты
    save(sorted_products[:NUM_POSITIONS_TO_PARSE], args.output, args.format)


    # посчитаем медиану
    print(f'Медианное значение цены в категории по адресу\n{parser.base_path.split("?")[0]}\n{calculate_mediana(sorted_products)} рублей.')

    # закроем браузер конкретного парсера
    parser.browser.quit()


def main():
    """
    Запуск с JSON-форматом, сортировкой по возрастанию и парсером parser1:
    python script.py -p parser1 -f json -s asc -o products
    Запуск с CSV-форматом и сортировкой по убыванию:
    python script.py --parser parser2 --format csv --sort desc --output report
    Получение справки по аргументам:
    """
    # Создание парсера аргументов командной строки
    parser = argparse.ArgumentParser(description="Программа для парсинга данных c сайта и сохранения в файл. Наберите -help для справки.")

    # Аргумент для выбора парсера
    parser.add_argument(
        "-p", "--parser",
        choices=["parser1", "parser2"],
        required=True,
        help="Выбор парсера: parser1 или parser2."
    )

    # Аргумент для выбора формата сохранения
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "xls"],
        required=True,
        help="Формат файла: csv или xls."
    )

    # Аргумент для выбора порядка сортировки. Необязательный.
    parser.add_argument(
        "-s", "--sort",
        choices=["asc", "desc"],
        default="asc",
        help="Сортировка: asc (по возрастанию) или desc (по убыванию)."
    )

    # Аргумент для выбора названия выходного файла
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Имя выходного файла без расширения."
    )

    args = parser.parse_args()

    # Вывод принятых аргументов (для отладки)
    #print(f"Выбранный парсер: {args.parser}")
    #print(f"Формат сохранения: {args.format}")
    #print(f"Порядок сортировки: {args.sort}")
    #print(f"Название файла: {args.output}.{args.format}")

    # Вызов функции обработки данных
    process_data(args)


if __name__ == "__main__":
    main()

