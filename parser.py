import re
import json
from bs4 import BeautifulSoup


SHANGHAI_DISTRICTS = {"浦东新区", "徐汇区", "长宁区", "静安区", "普陀区", "黄浦区",
                      "虹口区", "杨浦区", "闵行区", "宝山区", "嘉定区", "松江区", "青浦区", "奉贤区", "金山区", "崇明区"}


def parse_html_to_lines(filename: str):
    with open(filename, 'r') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    span_elems = soup.select("#js_content p")

    if len(span_elems) == 0:
        span_elems = soup.select("#ivs_content p")

    lines = []
    for span_elem in span_elems:
        text = span_elem.text
        if text.find("滑动查看更多") != -1:
            continue
        lines.append(span_elem.get_text())
    return lines


def extract_cases(line: str):
    regex1 = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增(\\d+)例本土(.*?)确诊病例(.*?)新增(\\d+)例本土无症状感染者.*?"
    m1 = re.match(regex1, line, re.IGNORECASE)
    if m1 is not None:
        (_, _, _, _, confirmed, _, _, asymptomatic) = m1.groups()
        return (int(confirmed), int(asymptomatic))

    regex2 = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增(\\d+)例本土无症状感染者.*?"
    m2 = re.match(regex2, line, re.IGNORECASE)
    if m2 is not None:
        (_, _, _, _, asymptomatic) = m2.groups()
        return (0, int(asymptomatic))

    regex3 = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增本土(.*?)确诊病例(\\d+)例(.*?)新增本土无症状感染者(\\d+)例.*?"
    m3 = re.match(regex3, line, re.IGNORECASE)
    if m3 is not None:
        (_, _, _, _, _, confirmed, _, asymptomatic) = m3.groups()
        return (int(confirmed), int(asymptomatic))

    regex4 = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增(\\d+)例本土(.*?)确诊病例(、|，|和)(\\d+)例本土无症状感染者.*?"
    m4 = re.match(regex4, line, re.IGNORECASE)
    if m4 is not None:
        (_, _, _, _, confirmed, _, _, asymptomatic) = m4.groups()
        return (int(confirmed), int(asymptomatic))

    return 0, 0


def parse_lines_to_json(lines):
    total = None
    districts = []
    regex_total = "市卫健委(.*?)通报：(.*?)(\\d+)年(\\d+)月(\\d+)日(.*?)新增本土新冠肺炎确诊病例(\\d+)例(.*?)和无症状感染者(\\d+)例.*?"
    regex_district = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增.*?"

    # a2c means asymptomatic to confirmed
    regex_a2c = "(.*?)(\\d+)例确诊病例为此前无症状感染者转归.*?"
    pattern_total = re.compile(regex_total, re.IGNORECASE)
    pattern_district = re.compile(regex_district, re.IGNORECASE)
    pattern_a2c = re.compile(regex_a2c, re.IGNORECASE)
    district_matched = None
    total_found = False
    a2c_found = False
    a2c = 0
    for line in lines:
        a2c_match = pattern_a2c.match(line)
        if not a2c_found and a2c_match is not None:
            a2c_found = True
            (_, a2c) = a2c_match.groups()

        total_match = pattern_total.match(line)
        if not total_found and total_match is not None:
            (_, _, y, m, d, _, confirmed, _, asymptomatic) = total_match.groups()
            total_found = True
            total = dict(
                date=f"{y}-{m:0>2}-{d:0>2}", confirmed=int(confirmed), asymptomatic=int(asymptomatic),
                total=int(confirmed)+int(asymptomatic)-int(a2c), asymptomatic_to_confirmed=int(a2c)
            )
            continue

        district_match = pattern_district.match(line)
        if district_match is not None:
            (_, _, _, district_name) = district_match.groups()
            (confirmed, asymptomatic) = extract_cases(line)
            district_name_clean = district_name.replace(
                "区无", "区").replace("无", "区").replace("区", "") + "区"
            district_matched = dict(
                district_name=district_name_clean, confirmed=int(confirmed),
                asymptomatic=int(asymptomatic), total=int(confirmed)+int(asymptomatic), places=[])
            districts.append(district_matched)
        else:
            if district_matched is None:
                continue

            if line.find("资料：") != -1 or line.find("编辑：") != -1 or line.find("消毒措施") != -1 or line.find("消毒等措施") != -1:
                district_matched = None
                continue

            place = line.strip().replace("、", "").replace(
                "，", "").replace("。", "")
            if place != "" and place not in SHANGHAI_DISTRICTS:
                district_matched['places'].append(place)

    districts_found = map(lambda d: d['district_name'], districts)
    districts_not_found = set(SHANGHAI_DISTRICTS) - set(districts_found)
    for district_not_found in districts_not_found:
        districts.append(dict(
            district_name=district_not_found, confirmed=0, asymptomatic=0, total=0, places=[]))

    total['districts'] = districts
    return total


def parse_html_to_json(filename: str):
    lines = parse_html_to_lines(filename)
    return parse_lines_to_json(lines)


def generate_all_data(urls_filename: str):
    with open(urls_filename, 'r') as f:
        urls = json.load(f)

    regex = "(\\d+)月(\\d+)日（(.*?)时）本市各区确诊病例、无症状感染者居住地信息.*?"
    pattern = re.compile(regex, re.IGNORECASE)
    for url in urls:
        text = url['text']
        m = pattern.match(text)
        if m is None:
            continue

        filename = "archived_html/" + url['filename']
        print(f"Parse: {text}, filename: {filename}")

        total = parse_html_to_json(filename)
        ret = json.dumps(total, ensure_ascii=False, indent=4,
                         separators=(',', ':'))

        with open(f"data/{total['date']}.json", 'w') as f:
            f.write(ret)


if __name__ == "__main__":
    # filename = "archived_html/67563db6c3ddc415a9d99abbe806efba.html"
    # total = get_json_data_from_file(filename)
    # ret = json.dumps(total, ensure_ascii=False,
    #                 indent = 4, separators = (',', ':'))
    # print(ret)

    urls_filename = "archived_html/urls.json"
    generate_all_data(urls_filename)
