import re
import json
from bs4 import BeautifulSoup


SHANGHAI_DISTRICTS = {"浦东新区", "徐汇区", "长宁区", "静安区", "普陀区", "闸北区", "黄浦区",
                      "虹口区", "杨浦区", "闵行区", "宝山区", "嘉定区", "松江区", "青浦区", "奉贤区", "金山区", "崇明区"}


def parse_to_lines(filename: str):
    with open(filename, 'r') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    span_elems = soup.select("#js_content section span")

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

    return 0, 0


def get_json_data(lines):
    total = None
    districts = []
    regex_total = "市卫健委(.*?)通报：(.*?)(\\d+)年(\\d+)月(\\d+)日(.*?)新增本土新冠肺炎确诊病例(\\d+)例(.*?)和无症状感染者(\\d+)例.*?"
    regex_district = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增.*?"
    pattern_total = re.compile(regex_total, re.IGNORECASE)
    pattern_district = re.compile(regex_district, re.IGNORECASE)
    district_matched = None
    total_found = False
    for line in lines:
        total_match = pattern_total.match(line)
        if not total_found and total_match is not None:
            (_, _, y, m, d, _, confirmed, _, asymptomatic) = total_match.groups()
            total_found = True
            total = dict(
                date=f"{y}-{m:0>2}-{d:0>2}", confirmed=int(confirmed), asymptomatic=int(asymptomatic),
                total=int(confirmed)+int(asymptomatic)
            )
            continue

        district_match = pattern_district.match(line)
        if district_match is not None:
            (_, _, _, district_name) = district_match.groups()
            (confirmed, asymptomatic) = extract_cases(line)
            district_matched = dict(
                district_name=district_name.replace("区无", "区"), confirmed=int(confirmed),
                asymptomatic=int(asymptomatic), total=int(confirmed)+int(asymptomatic), addresses=[])
            districts.append(district_matched)
        else:
            if district_matched is None:
                continue

            if line.find("资料：") != -1 or line.find("编辑：") != -1 or line.find("消毒措施") != -1 or line.find("消毒等措施") != -1:
                district_matched = None
                continue

            address = line.strip().replace("、", "").replace(
                "，", "").replace("。", "")
            if address != "" and address not in SHANGHAI_DISTRICTS:
                district_matched['addresses'].append(address)

    total['districts'] = districts
    return total


def get_json_data_from_file(filename: str):
    lines = parse_to_lines(filename)
    return get_json_data(lines)


def generate_data_from_urls(urls_filename: str):
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

        total = get_json_data_from_file(filename)
        ret = json.dumps(total, ensure_ascii=False, indent=4,
                         separators=(',', ':'))

        with open(f"data/{total['date']}.json", 'w') as f:
            f.write(ret)


if __name__ == "__main__":
    # filename = "archived_html/d52951915aaf51521046ddf7e70776f5.html"
    # total = get_json_data_from_file(filename)
    # ret = json.dumps(total, ensure_ascii=False,
    #                  indent=4, separators=(',', ':'))
    # print(ret)

    urls_filename = "archived_html/urls.json"
    generate_data_from_urls(urls_filename)
