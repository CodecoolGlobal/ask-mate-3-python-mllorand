from datetime import datetime


def convert_timestamp_to_date(entries):
    for entry in entries:
        entry["submission_time"] = datetime.fromtimestamp(int(entry["submission_time"]))\
                                                        .strftime("%Y-%m-%d <br> %H:%M:%S")
    return entries


def generate_timestamp():
    timestamp = int(datetime.now().timestamp())
    return timestamp
