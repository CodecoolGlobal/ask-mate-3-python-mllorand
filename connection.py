import csv


def read_csv(filename, header):
    try:
        with open(filename) as file:
            questions = [question for question in csv.DictReader(file)]
        return questions
    except FileNotFoundError:
        with open(filename, "w") as file:
            file.write(",".join(header))
            file.write("\n")
        return read_csv(filename, header)
