import json
import os


def write_file(content, filename):
    with open(filename, 'w') as f:
        f.write(content)


def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()


def get_data(filenames=None):
    new_cases = []
    if filenames is None:
        filenames = filter(lambda x: x.endswith("json"), os.listdir("./data"))
    sorted_filenames = sorted(filenames)
    for filename in sorted_filenames:
        case_by_date = json.loads(open(f"./data/{filename}").read())
        new_cases.append(case_by_date)

    return new_cases


def get_place_data():
    places = []
    filenames = filter(lambda x: x.endswith("json") and x != ("geo_cached.json"),
                       os.listdir("./data/place"))
    sorted_filenames = sorted(filenames)
    for filename in sorted_filenames:
        place = json.loads(open(f"./data/place/{filename}").read())
        places.extend(place)

    return places


def get_overview_data():
    new_cases = {}
    filenames = filter(lambda x: x.endswith("json"),
                       os.listdir("./data/overview"))
    sorted_filenames = sorted(filenames)[13:]
    for filename in sorted_filenames:
        case_by_date = json.loads(open(f"./data/overview/{filename}").read())
        new_cases[case_by_date['date']] = case_by_date

    return new_cases
