# coding: utf-8
# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

# Импортируем модули для работы с JSON и логами.
import json
import logging

# Импортируем подмодули Flask для запуска веб-сервиса.
from flask import Flask, request
app = Flask(__name__)


logging.basicConfig(level=logging.DEBUG)

# Хранилище данных о сессиях.
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

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(
        response,
        ensure_ascii=False,
        indent=2
    )

# Функция для непосредственной обработки диалога.
def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }

        res['response']['text'] = 'Привет путешественник! Хочешь ли ты изучить край нашей необъятной страны России?'
        # res['response']['buttons'] = get_suggests(user_id)
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'да',
        'хочу'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = 'Ну, тогда давай знакомиться. Как тебя зовут?'
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'никита'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = 'Очень приятно! Ну что, начнём нашу путешествие?'
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'да',
        'конечно'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = 'Первый вопрос. Знаменитые Ленские столбы возвышаются грозными утёсами на берегу одной из крупных рек Якутии. На какой реке они стоят?'
        res['response']['buttons'] = get_suggests(user_id, ['Индигирка', 'Лена', 'Калыма', 'Оленек'])
        return

    # Обрабатываем ответ пользователя.
    if req['request']['original_utterance'].lower() in [
        'лена'
    ]:
        # Пользователь согласился, прощаемся.
        res['response']['text'] = 'Это правильный ответ! Поздравляю! Перейдём к следующему вопросу. Форма этого памятника в виде трехгранного штыка. В каком городе он находится?'
        res['response']['buttons'] = get_suggests(user_id, ['Мурманск', 'Санкт-Петербург', 'Волгоград', 'Москва'])
        return


    # # Если нет, то убеждаем его купить слона!
    # res['response']['text'] = 'Все говорят "%s", а ты купи слона!' % (
    #     req['request']['original_utterance']
    # )
    # res['response']['buttons'] = get_suggests(user_id)

# # Функция возвращает две подсказки для ответа.
# def get_suggests(user_id):
#     session = sessionStorage[user_id]
#
#     # Выбираем две первые подсказки из массива.
#     suggests = [
#         {'title': suggest, 'hide': True}
#         for suggest in session['suggests'][:2]
#     ]
#
#     # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
#     session['suggests'] = session['suggests'][1:]
#     sessionStorage[user_id] = session
#
#     # Если осталась только одна подсказка, предлагаем подсказку
#     # со ссылкой на Яндекс.Маркет.
#     if len(suggests) < 2:
#         suggests.append({
#             "title": "Ладно",
#             "url": "https://market.yandex.ru/search?text=слон",
#             "hide": True
#         })
#
#     return suggests


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