import csv


def get_all_question():
    try:
        with open(QUESTION_FILE_PATH) as file:
            questions = [question for question in csv.DictReader(file)]
        return questions
    except FileNotFoundError:
        with open(QUESTION_FILE_PATH, "w") as file:
            file.write(",".join(QUESTION_HEADER))
            file.write("\n")
        return get_all_question()
