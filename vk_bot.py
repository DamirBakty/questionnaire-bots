import json
import random

import vk_api as vk
from environs import Env
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from question_helpers import get_new_questionnaire, check_answer
from redis_connection import get_redis_connection


def command_handler(event, vk_api, keyboard, r):
    message = event.text
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        if message == 'Новый вопрос':
            questionnaire = get_new_questionnaire()
            question = questionnaire['question']

            vk_api.messages.send(
                user_id=event.user_id,
                message=question,
                random_id=random.randint(1, 1000),
                keyboard=keyboard.get_keyboard()
            )

            question_json = json.dumps(questionnaire)
            r.set(event.user_id, question_json)
            return
        elif message == 'Сдаться':
            old_questionnaire = r.get(event.user_id)
            if not old_questionnaire:
                vk_api.messages.send(
                    user_id=event.user_id,
                    message='Вам еще не был задан вопрос',
                    random_id=random.randint(1, 1000),
                    keyboard=keyboard.get_keyboard()
                )
                return

            old_questionnaire = json.loads(old_questionnaire)
            answer = old_questionnaire['answer']

            vk_api.messages.send(
                user_id=event.user_id,
                message=f'Ответ на предыдущий вопрос:\n{answer}',
                random_id=random.randint(1, 1000),
                keyboard=keyboard.get_keyboard()
            )
            new_questionnaire = get_new_questionnaire()
            new_question = new_questionnaire['question']

            vk_api.messages.send(
                user_id=event.user_id,
                message=f'Новый вопрос:\n{new_question}',
                random_id=random.randint(1, 1000),
                keyboard=keyboard.get_keyboard()
            )

            question_json = json.dumps(new_questionnaire)
            r.set(event.user_id, question_json)
            return
        else:
            old_questionnaire = r.get(event.user_id)
            if not old_questionnaire:
                vk_api.messages.send(
                    user_id=event.user_id,
                    message='Я тебя не понимаю',
                    random_id=random.randint(1, 1000),
                    keyboard=keyboard.get_keyboard()
                )
                return
            else:
                old_questionnaire = json.loads(old_questionnaire)
                right_answer = old_questionnaire['answer']
                if check_answer(user_answer=message, right_answer=right_answer):
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
                        random_id=random.randint(1, 1000),
                        keyboard=keyboard.get_keyboard()
                    )
                    r.delete(event.user_id)
                    return
                else:
                    vk_api.messages.send(
                        user_id=event.user_id,
                        message='Неправильно… Попробуешь ещё раз?',
                        random_id=random.randint(1, 1000),
                        keyboard=keyboard.get_keyboard()
                    )
                    return


def main():
    env = Env()
    env.read_env()
    vk_bot_token = env.str('VK_BOT_TOKEN')
    redis_host = env.str("REDIS_HOST", 'localhost')
    redis_port = env.int("REDIS_PORT", '6379')
    redis_db = env.int("REDIS_DB", '0')

    r = get_redis_connection(redis_host, redis_port, redis_db)

    vk_session = vk.VkApi(token=vk_bot_token)
    vk_api = vk_session.get_api()
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            command_handler(event, vk_api, keyboard, r)


if __name__ == '__main__':
    main()
