import csv


def read_csv(file_path, header):
    try:
        with open(file_path) as file:
            entries = [entry for entry in csv.DictReader(file)]
        return entries
    except FileNotFoundError:
        with open(file_path, "w") as file:
            file.write(",".join(header))
            file.write("\n")
        return read_csv(file_path, header)


