import json
import os
from environs import Env


def main():
    env = Env()
    env.read_env()
    path_to_questions_directory = os.path.join(env.str('PATH_TO_QUESTIONS_DIRECTORY'), 'quiz-questions')

    questionnaires = read_all_questionnaires(path_to_questions_directory)

    texts = questionnaires.split('\n\n')

    questionnaire = []
    current_question = {}

    for text in texts:
        if 'Вопрос' in text:
            if current_question:
                questionnaire.append(current_question)
                current_question = {}

            current_question['question'] = text.replace('Вопрос', '').strip()

        elif 'Ответ' in text:
            current_question['answer'] = text.replace('Ответ', '').strip()

    if current_question:
        questionnaire.append(current_question)

    questions = extract_questions(questionnaire)

    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=4)


def extract_questions(questionnaire):
    questions = []
    for entry in questionnaire:
        question = entry.get('question', '').replace('\n', ' ').strip()
        answer = entry.get('answer', '').replace('\n', ' ').strip()

        if "Вопрос" in question:
            question = question.split('Вопрос', 1)[-1].strip()
        if "Ответ:" in answer:
            answer = answer.split('Ответ:', 1)[-1].strip()

        if ':' in question:
            question = question.split(':', 1)[-1].strip()

        questions.append({
            'question': question.replace('  ', ' '),
            'answer': answer[2:].replace('  ', ' ')
        })

    return questions


def read_all_questionnaires(directory):
    questionnaires = []

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)

            with open(file_path, "r", encoding='KOI8-R') as file:
                questionnaire = file.read()
                questionnaires.append(questionnaire)

    return ' '.join(questionnaires)


if __name__ == '__main__':
    main()
