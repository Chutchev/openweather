
""" OpenWeatherMap (экспорт)

Сделать скрипт, экспортирующий данные из базы данных погоды, 
созданной скриптом openweather.py. Экспорт происходит в формате CSV или JSON.

Скрипт запускается из командной строки и получает на входе:
    export_openweather.py --csv filename [<город>]
    export_openweather.py --json filename [<город>]
    export_openweather.py --html filename [<город>]
    
При выгрузке в html можно по коду погоды (weather.id) подтянуть 
соответствующие картинки отсюда:  http://openweathermap.org/weather-conditions

Экспорт происходит в файл filename.

Опционально можно задать в командной строке город. В этом случае 
экспортируются только данные по указанному городу. Если города нет в базе -
выводится соответствующее сообщение.

"""

import csv
import json
import sqlite3


def get_data_from_db():
    with sqlite3.connect("./openweather_db.db") as conn:
        cur = conn.cursor()
        data = cur.execute("""SELECT * FROM table_info_city""")
        strokes_from_db = data.fetchall()
    return strokes_from_db


def create_dictionary_for_json(strokes_from_db):
    list_for_json = []
    for id, name, date, temp, weather_id in strokes_from_db:
        list_for_json.append({'id': id, 'name': name, 'date': date, 'temp': temp, 'weather_id': weather_id})
    return list_for_json


def save_json(list_for_json):
    json_data = json.dumps(list_for_json, sort_keys=True, indent=4)
    with open("./openweather_json.json", 'w', encoding='utf-8') as f:
        f.write(json_data)


def main():
    strokes_from_db = get_data_from_db()
    list_for_json = create_dictionary_for_json(strokes_from_db)
    save_json(list_for_json)

if __name__ == "__main__":
    main()