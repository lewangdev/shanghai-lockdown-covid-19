import re
import json
from bs4 import BeautifulSoup


def parse_to_lines(filename: str):
    with open(filename, 'r') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    span_elems = soup.select("#js_content section span")

    lines = []
    for span_elem in span_elems:
        text = span_elem.text
        if text.find("滑动查看更多") != -1:
            continue
        lines.append(span_elem.get_text())
    return lines


if __name__ == "__main__":
    filename = "archived_html/22584a06e898fce7cda176c651650497.html"
    lines = parse_to_lines(filename)

    total = None
    districts = []
    regex_total = "市卫健委(.*?)通报：(.*?)(\\d+)年(\\d+)月(\\d+)日(.*?)新增本土新冠肺炎确诊病例(\\d+)例和无症状感染者(\\d+)例"
    regex_district = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增(\\d+)例本土确诊病例，新增(\\d+)例本土无症状感染者.*?"
    pattern_total = re.compile(regex_total, re.IGNORECASE)
    pattern_district = re.compile(regex_district, re.IGNORECASE)
    district_matched = None
    total_found = False
    for line in lines:
        total_match = pattern_total.match(line)
        if not total_found and total_match is not None:
            (_, _, y, m, d, _, confirmed, asymptomatic) = total_match.groups()
            total_found = True
            total = dict(
                date=f"{y}-{m}-{d}", confirmed=int(confirmed), asymptomatic=int(asymptomatic),
                total=int(confirmed)+int(asymptomatic)
            )
            continue

        district_match = pattern_district.match(line)
        if district_match is not None:
            (_, _, _, district_name,
             confirmed, asymptomatic) = district_match.groups()
            district_matched = dict(
                district_name=district_name, confirmed=int(confirmed),
                asymptomatic=int(asymptomatic), total=int(confirmed)+int(asymptomatic), addresses=[])
            districts.append(district_matched)
        else:
            if district_matched is None:
                continue

            if line.find("资料：") != -1 or line.find("编辑：") != -1 or line.find("消毒措施") != -1:
                continue

            address = line.strip().replace("、", "").replace(
                "，", "").replace("。", "")
            if address != "":
                district_matched['addresses'].append(address)

    total['districts'] = districts
    ret = json.dumps(total, ensure_ascii=False, indent=4,
                     separators=(',', ':'))
    print(ret)
