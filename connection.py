import csv


def read_csv(filename, header):
    try:
        with open(filename) as file:
            entries = [entry for entry in csv.DictReader(file)]
        return entries
    except FileNotFoundError:
        with open(filename, "w") as file:
            file.write(",".join(header))
            file.write("\n")
        return read_csv(filename, header)


