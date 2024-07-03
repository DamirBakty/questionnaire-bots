import json
from enum import Enum

import redis
from environs import Env
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

from utils import get_new_questionnaire, check_answer

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool)


class ConversationStates(Enum):
    ANSWER = 1
    QUESTION = 2
    KEYBOARD = 3
    SURRENDER = 4


def start(update: Update, context: CallbackContext):
    user = update.effective_user

    custom_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']
    ]

    reply_markup = ReplyKeyboardMarkup(
        custom_keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

    update.message.reply_text(
        text='Привет! я бот для викторин!',
        reply_markup=reply_markup
    )
    return ConversationStates.KEYBOARD


def surrender(update: Update, context: CallbackContext):
    user = update.effective_user
    old_questionnaire = r.get(user.id)
    if not old_questionnaire:
        update.message.reply_text(
            'Вам еще не был задан вопрос'
        )
        return ConversationStates.KEYBOARD

    old_questionnaire = json.loads(old_questionnaire)
    answer = old_questionnaire['answer']
    update.message.reply_text(
        f'Ответ на предыдущий вопрос:\n{answer}'
    )
    new_questionnaire = get_new_questionnaire()
    update.message.reply_text(
        f'Новый вопрос:\n{new_questionnaire["question"]}'
    )
    question_json = json.dumps(new_questionnaire)
    r.set(user.id, question_json)
    return ConversationStates.ANSWER


def keyboard_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text
    match message:
        case 'Новый вопрос':
            questionnaire = get_new_questionnaire()
            question = questionnaire['question']
            update.message.reply_text(
                question
            )
            question_json = json.dumps(questionnaire)
            r.set(user.id, question_json)
            return ConversationStates.ANSWER

        case 'Сдаться':
            return ConversationStates.SURRENDER

        case 'Мой счет':
            return ConversationStates.KEYBOARD

        case _:
            update.message.reply_text(
                'Я тебя не понимаю'
            )
            return ConversationStates.KEYBOARD


def answer_to_question(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text
    if message == 'Сдаться':
        return ConversationStates.SURRENDER

    questionnaire = json.loads(r.get(user.id))
    answer = questionnaire['answer']

    is_right_answer = check_answer(
        user_answer=message,
        right_answer=answer
    )

    if is_right_answer:
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        )
        r.delete(user.id)
        return ConversationStates.KEYBOARD

    else:
        update.message.reply_text(
            'Неправильно… Попробуешь ещё раз?'
        )

    return ConversationStates.ANSWER


def main() -> None:
    env = Env()
    env.read_env()
    tg_bot_token = env.str('TG_BOT_TOKEN')
    updater = Updater(tg_bot_token)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ConversationStates.KEYBOARD: [MessageHandler(Filters.text, keyboard_handler)],
            ConversationStates.ANSWER: [MessageHandler(Filters.text, answer_to_question)],
            ConversationStates.SURRENDER: [MessageHandler(Filters.text, surrender)],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()