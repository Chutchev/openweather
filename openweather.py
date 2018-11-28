
""" 
== OpenWeatherMap ==

OpenWeatherMap — онлайн-сервис, который предоставляет бесплатный API
 для доступа к данным о текущей погоде, прогнозам, для web-сервисов
 и мобильных приложений. Архивные данные доступны только на коммерческой основе.
 В качестве источника данных используются официальные метеорологические службы
 данные из метеостанций аэропортов, и данные с частных метеостанций.

Необходимо решить следующие задачи:

== Получение APPID ==
    Чтобы получать данные о погоде необходимо получить бесплатный APPID.
    
    Предлагается 2 варианта (по желанию):
    - получить APPID вручную
    - автоматизировать процесс получения APPID, 
    используя дополнительную библиотеку GRAB (pip install grab)

        Необходимо зарегистрироваться на сайте openweathermap.org:
        https://home.openweathermap.org/users/sign_up

        Войти на сайт по ссылке:
        https://home.openweathermap.org/users/sign_in

        Свой ключ "вытащить" со страницы отсюда:
        https://home.openweathermap.org/api_keys
        
        Ключ имеет смысл сохранить в локальный файл, например, "app.id"

        
== Получение списка городов ==
    Список городов может быть получен по ссылке:
    http://bulk.openweathermap.org/sample/city.list.json.gz
    
    Далее снова есть несколько вариантов (по желанию):
    - скачать и распаковать список вручную
    - автоматизировать скачивание (ulrlib) и распаковку списка 
     (воспользоваться модулем gzip 
      или распаковать внешним архиватором, воспользовавшись модулем subprocess)
    
    Список достаточно большой. Представляет собой JSON-строки:
{"_id":707860,"name":"Hurzuf","country":"UA","coord":{"lon":34.283333,"lat":44.549999}}
{"_id":519188,"name":"Novinki","country":"RU","coord":{"lon":37.666668,"lat":55.683334}}
    
    
== Получение погоды ==
    На основе списка городов можно делать запрос к сервису по id города. И тут как раз понадобится APPID.
        By city ID
        Examples of API calls:
        http://api.openweathermap.org/data/2.5/weather?id=2172797&appid=b1b15e88fa797225412429c1c50c122a

    Для получения температуры по Цельсию:
    http://api.openweathermap.org/data/2.5/weather?id=520068&units=metric&appid=b1b15e88fa797225412429c1c50c122a

    Для запроса по нескольким городам сразу:
    http://api.openweathermap.org/data/2.5/group?id=524901,703448,2643743&units=metric&appid=b1b15e88fa797225412429c1c50c122a


    Данные о погоде выдаются в JSON-формате
    {"coord":{"lon":38.44,"lat":55.87},
    "weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04n"}],
    "base":"cmc stations","main":{"temp":280.03,"pressure":1006,"humidity":83,
    "temp_min":273.15,"temp_max":284.55},"wind":{"speed":3.08,"deg":265,"gust":7.2},
    "rain":{"3h":0.015},"clouds":{"all":76},"dt":1465156452,
    "sys":{"type":3,"id":57233,"message":0.0024,"country":"RU","sunrise":1465087473,
    "sunset":1465149961},"id":520068,"name":"Noginsk","cod":200}    


== Сохранение данных в локальную БД ==    
Программа должна позволять:
1. Создавать файл базы данных SQLite со следующей структурой данных
   (если файла базы данных не существует):

    Погода
        id_города           INTEGER PRIMARY KEY
        Город               VARCHAR(255)
        Дата                DATE
        Температура         INTEGER
        id_погоды           INTEGER                 # weather.id из JSON-данных

2. Выводить список стран из файла и предлагать пользователю выбрать страну 
(ввиду того, что список городов и стран весьма велик
 имеет смысл запрашивать у пользователя имя города или страны
 и искать данные в списке доступных городов/стран (регуляркой))

3. Скачивать JSON (XML) файлы погоды в городах выбранной страны
4. Парсить последовательно каждый из файлов и добавлять данные о погоде в базу
   данных. Если данные для данного города и данного дня есть в базе - обновить
   температуру в существующей записи.


При повторном запуске скрипта:
- используется уже скачанный файл с городами;
- используется созданная база данных, новые данные добавляются и обновляются.


При работе с XML-файлами:

Доступ к данным в XML-файлах происходит через пространство имен:
<forecast ... xmlns="http://weather.yandex.ru/forecast ...>

Чтобы работать с пространствами имен удобно пользоваться такими функциями:

    # Получим пространство имен из первого тега:
    def gen_ns(tag):
        if tag.startswith('{'):
            ns, tag = tag.split('}')
            return ns[1:]
        else:
            return ''

    tree = ET.parse(f)
    root = tree.getroot()

    # Определим словарь с namespace
    namespaces = {'ns': gen_ns(root.tag)}

    # Ищем по дереву тегов
    for day in root.iterfind('ns:day', namespaces=namespaces):
        ...

"""
import json
import requests
import sqlite3
import datetime


def get_city_info(city, *city_list):
    for info_cities in city_list:
        for city_info_key, city_info_value in info_cities.items():
            if city == city_info_value:
                return info_cities


def parse_city_info(info, info_in_json, **city_info):
    try:
        for dictionary in city_info[info]:
            return dictionary[info_in_json]
    except TypeError:
        for key, value in city_info[info].items():
            if key == info_in_json:
                return value
    except AttributeError:
            return city_info[info]


def get_city_id(**city_info):
    return city_info['id']


def get_api():
    with open('./app.id', 'r', encoding='utf-8') as f:
        api = f.read()
    return api


def get_json_for_city(api, city, city_list):
    city_info = get_city_info(city, *city_list)
    city_id = get_city_id(**city_info)
    url = f"http://api.openweathermap.org/data/2.5/weather?id={city_id}&units=metric&appid={api}"
    city_data_json = requests.get(url)
    return city_data_json.json()


def read_json(filename):
    with open(f"./{filename}", 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    return data


def insert_info_to_db(**city_info):
    city_id = city_info['id']
    city_name = city_info['name']
    date_now = datetime.date.today()
    temperature = parse_city_info('main', 'temp', **city_info)
    weather_id = parse_city_info('weather', 'id', **city_info)
    params = (city_id, city_name, date_now, temperature, weather_id)
    with sqlite3.connect("openweather_db.db") as conn:
        conn.execute("INSERT INTO table_info_city (city_id, city_name, date_now, temperature, weather_id)"
                     " VALUES (?, ?, ?, ?, ?)", params)


def create_db():
    with sqlite3.connect("openweather_db.db") as conn:
        conn.execute("""CREATE TABLE table_info_city
        (
            city_id integer,
            city_name VARCHAR(255),
            date_now date ,
            temperature integer,
            weather_id integer 
        );""")


def select_city_db(name_city):
    with sqlite3.connect("openweather_db.db") as conn:
        cur = conn.cursor()
        data = cur.execute(f"SELECT * FROM table_info_city WHERE city_name='{name_city}'")
        strokes_city = data.fetchall()
    if len(strokes_city) != 0:
        return True
    else:
        return False


def update_city_db(**city_info):
    with sqlite3.connect("openweather_db.db") as conn:
        cur = conn.cursor()
        city_id = city_info['id']
        date_now = datetime.date.today()
        temperature = parse_city_info('main', 'temp', **city_info)
        cur.execute(f"""UPDATE table_info_city SET 
                            city_id={city_id}, 
                            date_now={date_now}, 
                            temperature = {temperature}""")

def main():
    city_list = read_json('city.list.json')
    api = get_api()
    city = input("Введите город транслитом\n").capitalize()
    city_info = get_json_for_city(api, city, city_list)
    try:
        create_db()
    except sqlite3.OperationalError:
        pass
    if select_city_db(city):
        update_city_db(**city_info)
    else:
        insert_info_to_db(**city_info)

if __name__ == "__main__":
    main()