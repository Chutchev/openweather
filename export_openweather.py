
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
import sys


def get_data_from_db(city):
    with sqlite3.connect("./openweather_db.db") as conn:
        cur = conn.cursor()
        data = cur.execute(f"""SELECT * FROM table_info_city where city_name='{city}'""")
        strokes_from_db = data.fetchall()
    return strokes_from_db


def create_dictionary_for_json(strokes_from_db):
    list_for_json = []
    for id, name, date, temp, weather_id in strokes_from_db:
        list_for_json.append({'id': id, 'name': name, 'date': date, 'temp': temp, 'weather_id': weather_id})
    return list_for_json


def save_json(list_for_output, filename):
    json_data = json.dumps(list_for_output, sort_keys=True, indent=4)
    with open(f"{filename}.json", 'w', encoding='utf-8') as f:
        f.write(json_data)

def save_csv(list_for_output, filename):
    for id, name, date, temp, weather_id in list_for_output:
        with open(f"{filename}.csv", "w", encoding='utf-8') as f:
            f.write(f"{id},{name},{date},{temp},{weather_id}")


#TODO Сделать вывод в html
def main():
    city = sys.argv[3]
    filename = sys.argv[2]
    output_type = sys.argv[1]
    strokes_from_db = get_data_from_db(city)
    if output_type == '--json':
        list_for_output = create_dictionary_for_json(strokes_from_db)
        save_json(list_for_output, filename)
    elif output_type == "--csv":
        list_for_output = get_data_from_db(city)
        save_csv(list_for_output, filename)
    elif output_type == '--html':
        pass

if __name__ == "__main__":
    main()