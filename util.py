import imp


import json
import os


def get_data():
    new_cases = []
    filenames = filter(lambda x: x.endswith("json"), os.listdir("./data"))
    sorted_filenames = sorted(filenames)
    for filename in sorted_filenames:
        case_by_date = json.loads(open(f"./data/{filename}").read())
        new_cases.append(case_by_date)

    return new_cases
