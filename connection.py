import csv


def read_csv(file_path, header):
    try:
        with open(file_path, encoding="utf-8") as file:
            entries = [entry for entry in csv.DictReader(file)]
        return entries
    except FileNotFoundError:
        with open(file_path, "w") as file:
            file.write(",".join(header))
            file.write("\n")
        return read_csv(file_path, header)


def write_csv(file_path, header, entries):
    with open(file_path, 'w', newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)


