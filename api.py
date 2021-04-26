from flask import Flask, request
import logging
import json
import random

# Первый
# комментарий
# тут инициализация
# flask
app = Flask(__name__)

# Здесь
# устанавливается
# тип логирования
# для удобства
logging.basicConfig(level=logging.INFO)

# Здесь
# указаны вопросы
# и ответы на них
cities = {
    'лена': ['Знаменитые Ленские столбы возвышаются грозными утёсами на берегу одной из крупных рек Якутии. На какой реке они стоят?',
             '1652229/2530bff99ec32a4bea34', ['Индигирка', 'Лена', 'Калыма', 'Оленек']],
    'москва': ['Форма этого памятника в виде трехгранного штыка. В каком городе он находится?', '213044/7a1793e70a7b6c5fc33b'],
    'санкт-петербург': ['Большевики мечтали снести этот памятник и вмест него воздвигнуть памятник Буденному или Фрунзе. В каком городе он установлен?',
                        '213044/fbe06584fa2c82359c26', ['Мурманск', 'Санкт-Петербург', 'Волгоград', 'Москва']],
    'сыктывкар': ['Это памятник загадочной букве Ö. Как думаете, в каком городе он находится?', '1521359/e4e55e736452bfde70a3',
                  ['Калининград', 'Великий Новгород', 'Сыктывкар']],
    'ярославль': ['Медведи на улицах городов — повод для шуток. Но в этом городе медведи и правда на каждом шагу. Где сделано фото?',
                  '997614/822c6e5c04b6878d73d9', ['Медвежьегорск', 'Ярославль', 'Петропавловск-Камчатский']],
    'карелия': ['Это памятник комару. Где кровопийц так много, что им даже поставили памятник?', '213044/6ad6c59be822daa5c264',
                ['Карелия', 'Сибирь', 'Болота Ленинградской области']],
    'сахалин': ['А где можно увидеть такую красоту?', '213044/a108f184353490187a17',
                ['Золотые ворота на Черном море', 'Сахалин', 'Кипр']],
    'алтай': ['Еще один пейзаж фантастической красоты. Знаете, где находится это место?', '1540737/569c0f455e6a827e2b82',
              ['Алтай', 'Иремель', 'Сахалин']],
    # 'вашингтон': ['А теперь — настоящий космос. В каком музее встретишь подобный экспонат?', '1540737/b8f160070f2fe2d17b77',
    #               ['Москва', 'Калуга', 'Вашингтон']],
    'краснодар': ['В одном из российских городов установлен памятник героям комедии Гайдая про приключения Шурика. Как думаете, где именно?',
                  '213044/0669ff936e1f095ab31e', ['Москва', 'Краснодар', 'Крым']],
    'камчатка': ['Сможете угадать, где находятся эти древние деревянные фигуры?', '937455/b8609e98c38dbc567fb1',
                 ['Камчатка', 'Байкал', 'Урал']]
}

# Инициализируем хранилище.
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





# Главная ветка кода.
def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,  # здесь будет храниться имя
            'game_started': False
        # здесь информация о том, что пользователь начал игру. По умолчанию False
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            # создаём пустой массив, в который будем записывать города, которые пользователь уже отгадал
            sessionStorage[user_id]['guessed_cities'] = []
            # как видно из предыдущего навыка, сюда мы попали, потому что пользователь написал своем имя.
            # Предлагаем ему сыграть и два варианта ответа "Да" и "Нет".
            res['response'][
                'text'] = f'Приятно познакомиться, {first_name.title()}. Я - Алиса. Хочешь ли ты изучить края нашей необъятной страны?'
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
            # игра не начата, значит мы ожидаем ответ на предложение сыграть.
            if 'да' in req['request']['nlu']['tokens']:
                # если пользователь согласен, то проверяем не отгадал ли он уже все города.
                # По схеме можно увидеть, что здесь окажутся и пользователи, которые уже отгадывали города
                if len(sessionStorage[user_id]['guessed_cities']) == len(cities):
                    # если все три города отгаданы, то заканчиваем игру
                    res['response']['text'] = 'Ты отгадал все города!'
                    res['response']['button'] = get_url_suggests(user_id, [['Открыть код',
                                                                'https://github.com/1thenikita/EdgesOfOurRussia/']])
                    res['end_session'] = True
                else:
                    # если есть неотгаданные города, то продолжаем игру
                    sessionStorage[user_id]['game_started'] = True
                    # номер попытки, чтобы показывать фото по порядку
                    sessionStorage[user_id]['attempt'] = 1
                    # функция, которая выбирает город для игры и показывает фото
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






# Функция запуска игры.
def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    if attempt == 1:
        # если попытка первая, то случайным образом выбираем город для гадания
        city = random.choice(list(cities))
        # выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
        while city in sessionStorage[user_id]['guessed_cities']:
            city = random.choice(list(cities))
        # записываем город в информацию о пользователе
        sessionStorage[user_id]['city'] = city
        # добавляем в ответ картинку
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = cities[city][0]
        res['response']['card']['image_id'] = cities[city][1]
        res['response']['text'] = 'Тогда сыграем!'
        res['response']['buttons'] = get_suggests(user_id, cities[city][2])
    else:
        # сюда попадаем, если попытка отгадать не первая
        city = sessionStorage[user_id]['city']
        # проверяем есть ли правильный ответ в сообщение
        if get_city(req).lower() == city:
            # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
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
            # если нет
            if attempt == 3:
                # если попытка третья, то значит, что все картинки мы показали.
                # В этом случае говорим ответ пользователю,
                # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                # Обратите внимание на этот шаг на схеме.
                res['response']['text'] = f'Вы пытались. Это {city.title()}. Сыграем ещё?'
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                return
            else:
                # иначе показываем следующую картинку
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = f'Ещё раз. {cities[city][0]}'
                res['response']['card']['image_id'] = cities[city][1]
                res['response']['text'] = 'А вот и не угадал!'
                res['response']['buttons'] = get_suggests(user_id, cities[city][2])
    # увеличиваем номер попытки доля следующего шага
    sessionStorage[user_id]['attempt'] += 1






# Функция возвращает город для ответа.
def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO, то пытаемся получить город(city), если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)






# Функция возвращает имя пользователя для ответа.
def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
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







# Функция возвращает подсказки для перехода по ссылке.
def get_url_suggests(user_id, _suggest):
    # Открываем сессию пользователя
    session = sessionStorage[user_id]

    # Обнуляем массив с подсказками.
    suggests = session['suggests'] = []

    # Через цикл добавляем подсказки в массив
    for i in range(len(_suggest)):
        suggests.append({
            "title": _suggest[i][0],
            "url": _suggest[i][1],
            "hide": True
        })

    # Возвращаем подсказки
    return suggests






# Запуск для дебага.
# if __name__ == '__main__':
#     app.run()