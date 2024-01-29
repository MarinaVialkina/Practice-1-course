import sys
import time
import requests #библиотека для составления HTTP-запросов
from bs4 import BeautifulSoup
import pprint
from fake_useragent import UserAgent

session = requests.Session()
headers = {'User-Agent': UserAgent().random}

login = str(input('Ввод логина:'))
password = str(input('Ввод пароля:'))
data = {
        'redirect':	"https://rutracker.org/forum/viewtopic.php?t=6330559",
        'login_username': login,
        'login_password': password,
        'login': "%C2%F5%EE%E4"
}

#Авторизация
session.get('https://rutracker.org/forum/index.php', headers=headers) #Вышли на главную
respons = session.get('https://rutracker.org/forum/login.php', headers=headers).text # Вышли на страницу авторизации
response = session.post('https://rutracker.org/forum/login.php', data=data, headers=headers).text #Авторизация

#Проверка входа в аккаунт.
r = session.get('https://rutracker.org/forum/index.php', headers=headers, params=None).text
s = BeautifulSoup(r, 'html.parser')
icon = s.find('img', class_='log-out-icon')
if icon == None:
    print('Неверный логин или пароль!')
    session.close()
    sys.exit()




def url_request():
    '''Функция создаёт url по запросу.'''
    global request
    request = input('Ввод запроса:')
    url = f'https://rutracker.org/forum/tracker.php?nm={request}'
    return url


def url_each_pages(html):
    '''Функция возвращает url следущей страницы результатов запроса.'''
    soup = BeautifulSoup(html, 'html.parser')
    all_pages = soup.find_all('a', class_='pg')
    for one_page in all_pages:
        if one_page.get_text() == str(page + 1):
            url = 'https://rutracker.org/forum/' + one_page.get('href')
            return url


def get_html(url, params = None):
    '''Функция возвращает html по имеющийся ссылке.'''
    r = session.get(url, headers=headers, params=params)
    return r


def get_pages_count(html):
    '''Функция считает кол-во страниц с выдаваемыми результатами, макс. кол-во результатов.'''
    soup = BeautifulSoup(html, 'html.parser')
    max_result_count = soup.find('p', class_="med bold").get_text()
    max_result_count = int(max_result_count[21:-11])
    pagination_is = soup.find('p', class_="small bold")
    if pagination_is:
        pagination_is = soup.find('p', class_="small bold")
        pagination = pagination_is.find_all('a')
        return int(pagination[-2].get_text()), max_result_count
    else:
        return 1, max_result_count


def get_content(html, number_result, k):
    '''Функция формирует блок информации по каждому результату и возвращает: каталог результатов одной страницы,
    номер паследнего результата,словарь(номер результата: id рузультата) и k-счётчик добаленных результатов.'''
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('tr', class_='tCenter hl-tr')

    catalog_one_page = [] #каталог результатов одной страницы
    id_result_one_page = {} #словарь(номер результата: id рузультата)

    for item in items:
        if k < result_count:
            k +=1
            idd = item.get('data-topic_id')
            id_result_one_page[number_result] = idd

            one_result = {} #Блок информации по одному результату

            one_result['HОМЕР РЕЗУЛЬТАТА'] = number_result

            status = item.find_all('td', class_='row1 t-ico')[-1].get('title')
            one_result['Статус:'] = status

            forum = item.find('a', class_='gen f ts-text').get_text()
            one_result['Форум:'] = forum

            topic = item.find('div', class_='wbr t-title').get_text()[1:-1]
            one_result['Тема:'] = topic

            author = item.find('a', class_="med ts-text").get_text()
            one_result['Автор'] = author

            size = item.find('a', class_="small tr-dl dl-stub").get_text()
            one_result['Размер:'] = size

            sidd = item.find('td', class_="row4 nowrap").get('data-ts_text')
            one_result['Сиды:'] = sidd

            lichi = item.find('td', class_="row4 leechmed bold").get_text()
            one_result['Личи:'] = lichi

            torrent_downloaded = item.find('td', class_="row4 small number-format").get_text()
            one_result['Торрент скачан:'] = torrent_downloaded

            added = item.find('td', class_="row4 small nowrap").get_text()[2:10]
            one_result['Добавлен:'] = added

            number_result += 1
            catalog_one_page.append(one_result)
        else:
            break
    return catalog_one_page, number_result, id_result_one_page, k

def find_downloded_file(HTML):
    '''Функция находит файл для скачивания по id выбранного результата и скачивает файл.'''
    soup = BeautifulSoup(HTML, 'html.parser')
    items = soup.find_all('tr', class_='tCenter hl-tr')
    for item in items:
        if item.get('data-topic_id') == id_downloaded:
            url_file = 'https://rutracker.org/forum/' + item.find('a', class_="small tr-dl dl-stub").get('href')
            file_bytes = session.get(url_file, headers=headers, params=None).content
            with open('file.torrent', 'wb') as file:
                file.write(file_bytes)
                print('Файл скачен.')







def parse():
    '''Функция осуществляет поиск торрент-файлов и их скачивание. Парсинг данных с сайта.'''
    global number_result, page, pages_count, k, result_count, id_downloaded
    url = url_request()
    html = get_html(url)
    HTML = html
    if html.status_code == 200:
        catalog = []
        pages_count, max_result_count = get_pages_count(html.text)
        result_count = int(input(f'Кол-во выдаваемых результатов за раз (Не более {max_result_count}):'))
        if result_count > max_result_count:
            while result_count >max_result_count:
                print(f'Макс. кол-во результатов меньше {result_count}')
                result_count = int(input(f'Кол-во выдаваемых результатов за раз (Не более {max_result_count}):'))
        number_result = 1
        id_result = {}
        k = 0
        for page in range(1, pages_count+1):
            if k < result_count:
                print(f'Парсинг страницы {page}')

                catalog_one_page, number_result, id_result_one_page, k = get_content(html.text, number_result, k)

                catalog.append(catalog_one_page)
                id_result.update(id_result_one_page)
                time.sleep(1)
                if page != pages_count:
                    url = url_each_pages(html.text)
                    html = get_html(url)
            else:
                break
        for a in catalog:
            for b in a:
                pprint.pprint(b)
                print('''
                
                ''')

        number_downloaded = int(input('Номер результата для скачивания торрента:'))
        id_downloaded = id_result.get(number_downloaded)

        for page in range(1, pages_count+1):
            find_downloded_file(HTML.text)
            if page != pages_count:
                    URL = url_each_pages(HTML.text)
                    HTML = get_html(URL)
    else:
        print('Error')






parse()

