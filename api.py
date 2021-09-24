from flask import Flask, request
import logging
import json
import random
from res.cities import cities

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


# Задаем параметры приложения Flask.
@app.route("/", methods=['POST'])
def main():
    # Функция получает тело запроса и возвращает ответ.
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(response, request.json)
    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    # Инициализируем сессию.
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,  # Имя пользователя
            'game_started': False  # Начал ли пользователь игру. По умолчанию False
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req) # Получаем имя.
        if first_name is None: # Если указано не существующее имя, то переспрашиваем.
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            # Создаём пустой массив, в который будем записывать города, которые пользователь уже отгадал
            sessionStorage[user_id]['guessed_cities'] = []
            # Как видно выше, сюда мы попали, потому что пользователь написал своем имя.
            # Предлагаем ему сыграть и два варианта ответа "Да" и "Нет".
            res['response'][
                'text'] = f'Приятно познакомиться, {first_name.title()}. Я - Алиса. Хочешь ли ты изучить края нашей ' \
                          f'необъятной страны? '
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                },
                {
                    'title': 'Нет',
                    'hide': True
                }
            ]
    else:
        # У нас уже есть имя, и теперь мы ожидаем ответ на предложение сыграть.
        # В sessionStorage[user_id]['game_started'] хранится True или False в зависимости от того,
        # начал пользователь игру или нет.
        if not sessionStorage[user_id]['game_started']:
            # Игра не начата, значит мы ожидаем ответ на предложение сыграть.
            if 'да' in req['request']['nlu']['tokens']:
                # Если пользователь согласен, то проверяем не отгадал ли он уже все города.
                # По схеме можно увидеть, что здесь окажутся и пользователи, которые уже отгадывали города
                if len(sessionStorage[user_id]['guessed_cities']) == 12:
                    # Если все три города отгаданы, то заканчиваем игру
                    res['response']['text'] = 'Ты отгадал все города!'
                    res['end_session'] = True
                else:
                    # Если есть неотгаданные города, то продолжаем игру
                    sessionStorage[user_id]['game_started'] = True
                    # Номер попытки, чтобы показывать фото по порядку
                    sessionStorage[user_id]['attempt'] = 1
                    # Функция, которая выбирает город для игры и показывает фото
                    play_game(res, req)
            elif 'нет' in req['request']['nlu']['tokens']:
                res['response']['text'] = 'Ну и ладно!'
                res['end_session'] = True
            else:
                res['response']['text'] = 'Не поняла ответа! Так да или нет?'
                res['response']['buttons'] = [
                    {
                        'title': 'Да',
                        'hide': True
                    },
                    {
                        'title': 'Нет',
                        'hide': True
                    }
                ]
        else:
            play_game(res, req)


# Функция начинает игру.
def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        # Если попытка первая, то случайным образом выбираем город для гадания
        city = random.choice(list(cities))
        # Выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        # Записываем город в информацию о пользователе
        sessionStorage[user_id]['city'] = city
        # Добавляем в ответ картинку
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = cities[city][attempt - 1]
        res['response']['card']['image_id'] = cities[city][attempt]
        res['response']['text'] = 'Тогда сыграем!'
        res['response']['buttons'] = get_suggests(user_id, cities[city][attempt + 1])
    else:
        # Сюда попадаем, если попытка отгадать не первая
        city = sessionStorage[user_id]['city']
        # Проверяем есть ли правильный ответ в сообщение
        if get_city(req).lower() == city:
            # Если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
            # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
            res['response']['text'] = 'Правильно! Сыграем ещё?'
            sessionStorage[user_id]['guessed_cities'].append(city)
            res['response']['buttons'] = [
                {
                    'title': 'Да',
                    'hide': True
                }
            ]
            sessionStorage[user_id]['game_started'] = False
            return
        else:
            # Если нет
            if attempt == 3:
                # Если попытка третья, то значит, что все картинки мы показали.
                # В этом случае говорим ответ пользователю,
                # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                # Обратите внимание на этот шаг на схеме.
                res['response']['text'] = f'Вы пытались. Это {city.title()}. Сыграем ещё?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                # Иначе показываем следующую картинку
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Неправильно. Вот тебе дополнительное фото'
                res['response']['card']['image_id'] = cities[city][attempt - 1]
                res['response']['text'] = 'А вот и не угадал!'
                res['response']['buttons'] = get_suggests(user_id, cities[city][attempt])
    # Увеличиваем номер попытки доля следующего шага
    sessionStorage[user_id]['attempt'] += 1


# Функция возвращает указанный город.
def get_city(req):
    # Перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # Если тип YANDEX.GEO, то пытаемся получить город(city), если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # Возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


# Функция возвращает имя пользователя.
def get_first_name(req):
    # Перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # Находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


# Функция возвращает подсказки для ответа.
def get_suggests(user_id, _suggest):
    # Открываем сессию пользователя
    session = sessionStorage[user_id]

    # Обнуляем массив с подсказками.
    suggests = []

    # Через цикл добавляем подсказки в массив
    for i in range(len(_suggest)):
        suggests.append({
            "title": _suggest[i],
            "hide": True
        })

    # Возвращаем подсказки
    return suggests


# Запуск бота.
if __name__ == '__main__':
    app.run()
