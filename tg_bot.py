import json
from enum import Enum

from environs import Env
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    RegexHandler

from question_helpers import get_new_questionnaire, check_answer
from redis_connection import get_redis_connection


class ConversationStates(Enum):
    ANSWER = 1
    CHOOSE = 2
    SURRENDER = 3


def start(update: Update, context: CallbackContext):
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
    return ConversationStates.CHOOSE


def surrender(update: Update, context: CallbackContext):
    user = update.effective_user
    r = context.bot_data.get('redis_connection')

    old_questionnaire = r.get(user.id)
    if not old_questionnaire:
        update.message.reply_text(
            'Вам еще не был задан вопрос'
        )
        return ConversationStates.CHOOSE

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


def get_new_question(update: Update, context: CallbackContext):
    user = update.effective_user
    questionnaire = get_new_questionnaire()
    r = context.bot_data.get('redis_connection')
    question = questionnaire['question']
    update.message.reply_text(
        question
    )
    question_json = json.dumps(questionnaire)
    r.set(user.id, question_json)
    return ConversationStates.ANSWER


def answer_to_question(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text
    r = context.bot_data.get('redis_connection')

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
        return ConversationStates.CHOOSE

    else:
        update.message.reply_text(
            'Неправильно… Попробуешь ещё раз?'
        )
        return ConversationStates.ANSWER


def main() -> None:
    env = Env()
    env.read_env()
    tg_bot_token = env.str('TG_BOT_TOKEN')
    redis_host = env.str("REDIS_HOST", 'localhost')
    redis_port = env.int("REDIS_PORT", '6379')
    redis_db = env.int("REDIS_DB", '0')

    r = get_redis_connection(redis_host, redis_port, redis_db)
    updater = Updater(tg_bot_token)

    dispatcher = updater.dispatcher
    dispatcher.bot_data['redis_connection'] = r

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ConversationStates.CHOOSE: [
                MessageHandler(Filters.regex('^Новый вопрос$'), get_new_question)
            ],

            ConversationStates.SURRENDER: [
                MessageHandler(Filters.regex('^Сдаться$'), surrender)
            ],

            ConversationStates.ANSWER: [
                MessageHandler(Filters.text, answer_to_question)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
