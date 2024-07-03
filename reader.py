import json
import os


def main():
    all_text = read_all_txt_files('quiz-questions')

    text_list = all_text.split('\n\n')

    questionnaire = []
    current_question = {}
    is_question = False

    for text in text_list:
        if 'Вопрос' in text:
            if current_question:
                questionnaire.append(current_question)
                current_question = {}

            is_question = True
            current_question['question'] = text.replace('Вопрос', '').strip()

        elif 'Ответ' in text:
            is_question = False
            current_question['answer'] = text.replace('Ответ', '').strip()

    if current_question:
        questionnaire.append(current_question)

    questions_dict = get_only_text(questionnaire)

    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(questions_dict, f, ensure_ascii=False, indent=4)


def get_only_text(questionnaire):
    text_dict = []
    for entry in questionnaire:
        question = entry.get('question', '').replace('\n', ' ').strip()
        answer = entry.get('answer', '').replace('\n', ' ').strip()

        if "Вопрос" in question:
            question = question.split('Вопрос', 1)[-1].strip()
        if "Ответ:" in answer:
            answer = answer.split('Ответ:', 1)[-1].strip()

        if ':' in question:
            question = question.split(':', 1)[-1].strip()

        text_dict.append({
            'question': question.replace('  ', ' '),
            'answer': answer[2:].replace('  ', ' ')
        })

    return text_dict


def read_all_txt_files(directory):
    all_text = []

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)

            with open(file_path, "r", encoding='KOI8-R') as file:
                text = file.read()
                all_text.append(text)

    return ' '.join(all_text)


if __name__ == '__main__':
    main()
