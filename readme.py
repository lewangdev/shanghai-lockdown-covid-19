from jinja2 import Environment, FileSystemLoader
from util import get_data

if __name__ == "__main__":
    # Get data
    new_cases = get_data()

    # Init jinja2
    env = Environment(loader=FileSystemLoader("."))
    env.trim_blocks = True
    env.lstrip_blocks = True

    total = 0
    cases = []
    for new_case in new_cases:
        total = new_case["total"] + total
        cases.append(dict(date=new_case["date"], total=total))

    # District data
    district_new_cases_dict = {}
    for new_case in new_cases:
        for district in new_case["districts"]:
            district_name = district['district_name']
            district_new_cases = district_new_cases_dict.get(district_name, [])
            district_new_cases.append(
                dict(date=new_case["date"], total=district['total'],
                     place_count=len(district['places'])))

    content = env.get_template(
        "README.md.j2").render(new_cases=sorted(new_cases, key=lambda x: x['date'], reverse=True),
                               cases=sorted(cases, key=lambda x: x['date'], reverse=True))

    with open("README.md", "w") as f:
        f.write(content)
