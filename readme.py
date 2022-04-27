from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from util import get_data, get_overview_data


def generate_readme_file():
    # Get data
    overview_data = get_overview_data()
    new_cases = get_data()

    # Init jinja2
    env = Environment(loader=FileSystemLoader("."))
    env.trim_blocks = True
    env.lstrip_blocks = True

    # Cases
    total = 0
    deaths = 0
    cases = []
    for new_case in new_cases:
        if overview_data.get(new_case['date']) is None:
            new_case['deaths'] = 0
        else:
            new_case['deaths'] = overview_data[new_case['date']].get(
                'deaths', 0)
        total = new_case["total"] + total
        deaths = new_case['deaths'] + deaths
        cases.append(dict(date=new_case["date"], total=total, deaths=deaths))

    # District data
    district_new_cases_dict = {}
    for new_case in new_cases:
        for district in new_case["districts"]:
            district_name = district['district_name']
            district_new_cases = district_new_cases_dict.get(district_name, [])
            district_total = 0
            if len(district_new_cases) > 0:
                district_total = district_new_cases[-1]["total"]
            district_new_cases.append(
                dict(date=new_case["date"], new_case=district['total'],
                     total=district['total'] + district_total,
                     place_count=len(district['places'])))
            district_new_cases_dict[district_name] = district_new_cases

    # Order by date
    cases_by_date = {}
    district_names = district_new_cases_dict.keys()
    for district_name in district_names:
        cases_by_district = district_new_cases_dict[district_name]
        for case in cases_by_district:
            cases_by_date[case["date"]] = cases_by_date.get(case["date"], [])
            cases_by_date[case["date"]].append(case)

    content = env.get_template(
        "README.md.j2").render(new_cases=sorted(new_cases, key=lambda x: x['date'], reverse=True),
                               cases=sorted(
                                   cases, key=lambda x: x['date'], reverse=True),
                               cases_by_date=cases_by_date,
                               district_names=district_names,
                               current_date=datetime.now().strftime("%d/%m/%Y"))

    with open("README.md", "w") as f:
        f.write(content)


if __name__ == "__main__":
    generate_readme_file()
