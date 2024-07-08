import json
import random


def check_answer(user_answer, right_answer):
    right_answer = extract_answer(right_answer).lower()
    user_answer = user_answer.lower().replace('.', '')
    return user_answer == right_answer


def get_new_questionnaire():
    with open('questions.json', 'r') as f:
        questions = json.load(f)
    questionnaire = random.choice(questions)
    return questionnaire


def extract_answer(answer):
    preprocessed_answer = []
    inside_parentheses = False

    for char in answer:
        if not inside_parentheses:
            preprocessed_answer.append(char)

        if char in '([{':
            inside_parentheses = True
        elif char in ')]}':
            inside_parentheses = False

    result = ''.join(preprocessed_answer).strip().lower()
    result = result.replace('\\', '')
    result = result.replace('.', '')
    result = result.replace('"', '')
    return result
