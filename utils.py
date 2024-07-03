import json
import random


def check_answer(user_answer, right_answer):
    right_answer = get_only_answer(right_answer).lower()
    user_answer = user_answer.lower().replace('.', '')
    return user_answer == right_answer


def get_new_questionnaire():
    with open('questions.json', 'r') as f:
        questions = json.load(f)
    number = random.randint(0, len(questions) - 1)
    questionnaire = questions[number]
    return questionnaire


def get_only_answer(answer):
    preprocessed_answer = []
    inside_parentheses = False

    for char in answer:
        if char == '(' or char == '[' or char == '{':
            inside_parentheses = True
        elif char == ')' or char == ']' or char == '}':
            inside_parentheses = False
        elif not inside_parentheses:
            preprocessed_answer.append(char)

    result = ''.join(preprocessed_answer).strip().lower()
    result = result.replace('\\', '')
    result = result.replace('.', '')
    result = result.replace('"', '')
    return result
