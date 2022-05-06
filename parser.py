import re
import json
from bs4 import BeautifulSoup

from crawler import get_urls_crawled


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
    regex1 = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增(\\d+)例(.*?)病例(.*?)新增(\\d+)例(.*?)无症状感染者.*?"
    m1 = re.match(regex1, line, re.IGNORECASE)
    if m1 is not None:
        (_, _, _, _, confirmed, _, _, asymptomatic, _) = m1.groups()
        return (int(confirmed), int(asymptomatic))

    regex2 = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增(\\d+)[例]{0,1}本土无症状感染者.*?"
    m2 = re.match(regex2, line, re.IGNORECASE)
    if m2 is not None:
        (_, _, _, _, asymptomatic) = m2.groups()
        return (0, int(asymptomatic))

    regex3 = "(\\d+)年(\\d+)月(\\d+)日，(.*?)新增本土(.*?)确诊病例(\\d+)例(.*?)新增本土无症状感染者(\\d+)例.*?"
    m3 = re.match(regex3, line, re.IGNORECASE)
    if m3 is not None:
        (_, _, _, _, _, confirmed, _, asymptomatic) = m3.groups()
        return (int(confirmed), int(asymptomatic))

    regex4 = "(\\d+)年(\\d+)月(\\d+)日(.*?)，(.*?)新增(\\d+)例(.*?)确诊病例(、|，|和)(\\d+)例(.*?)无症状感染者.*?"
    m4 = re.match(regex4, line, re.IGNORECASE)
    if m4 is not None:
        (_, _, _, _, _, confirmed, _, _, asymptomatic, _) = m4.groups()
        return (int(confirmed), int(asymptomatic))

    regex5 = "(\\d+)年(\\d+)月(\\d+)日(.*?)，(.*?)无新增(.*?)本土(.*?)确诊病例(、|，|和)(.*?)(\\d+)例(.*?)无症状感染者.*?"
    m5 = re.match(regex5, line, re.IGNORECASE)
    if m5 is not None:
        (_, _, _, _, _, _, _, _, _, asymptomatic, _) = m5.groups()
        return (0, int(asymptomatic))

    regex6 = "(\\d+)月(\\d+)日，(.*?)新增(\\d+)例(.*?)确诊病例(、|，|和)(.*?)(\\d+)例(.*?)无症状感染者.*?"
    m6 = re.match(regex6, line, re.IGNORECASE)
    if m6 is not None:
        (_, _, _, confirmed, _, _, _, asymptomatic, _) = m6.groups()
        return (int(confirmed), int(asymptomatic))

    return 0, 0


def extract_a2c(line: str):
    regex_a2c = "(.*?)(\\d+)例确诊病例(.*?)无症状感染者转归.*?"
    a2c = 0
    a2c_match = re.match(regex_a2c, line, re.IGNORECASE)
    if a2c_match is not None:
        (_, a2c, _) = a2c_match.groups()
        return True, int(a2c)

    regex_a2c2 = "(.*?)含既往无症状感染者转为确诊病例(\\d+)例.*?"
    a2c_match2 = re.match(regex_a2c2, line, re.IGNORECASE)
    if a2c_match2 is not None:
        (_, a2c) = a2c_match2.groups()
        return True, int(a2c)

    return False, 0


def parse_lines_to_json(lines):
    total = None
    districts = []
    regex_total = "市卫健委(.*?)通报：(.*?)(\\d+)年(\\d+)月(\\d+)日(.*?)新增本土新冠肺炎确诊病例(\\d+)(.*?)和无症状感染者(\\d+)例.*?"
    regex_district = "^(\\d+年)?(\\d+)月(\\d+)日(.*?)，(.*?)新增.*?"

    pattern_total = re.compile(regex_total, re.IGNORECASE)
    pattern_district = re.compile(regex_district, re.IGNORECASE)
    district_matched = None
    total_found = False
    # a2c means asymptomatic to confirmed
    a2c_found = False
    a2c = 0
    for line in lines:
        if not a2c_found:
            (a2c_found, a2c) = extract_a2c(line)

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
            (_, _, _, _, district_name) = district_match.groups()
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


def generate_json_files(urls):
    regex = "(.*?)月(\\d+)日（(.*?)时）本市各区确诊病例、无症状感染者居住地信息.*?"
    pattern = re.compile(regex, re.IGNORECASE)
    json_filenames = []
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
        json_filename = f"{total['date']}.json"
        with open(f"data/{json_filename}", 'w') as f:
            f.write(ret)
        json_filenames.append(json_filename)
    return json_filenames


if __name__ == "__main__":
    filename = "archived_html/000680e8edce1f4040793950391eb1ac.html"
    total = parse_html_to_json(filename)
    ret = json.dumps(total, ensure_ascii=False,
                     indent=4, separators=(',', ':'))
    with open(f"data/{total['date']}.json", 'w') as f:
        f.write(ret)
    print(ret)

    # urls = get_urls_crawled()
    # generate_json_files(urls)

    ss = ["2022年4月26日，崇明区新增14例新冠肺炎本土确诊病例，其中12例居住于闭环管理的建筑工地；新增453例无症状感染者，其中447例居住于闭环管理的建筑工地。其余分别居住于：",
          "2022年4月26日，奉贤区新增2例本土新冠病例，新增11例本土无症状感染者。上述病例均在隔离管控中发现，分别居住于：",
          "2022年4月23日，金山区新增44本土无症状感染者，其中部分病例之前已落实管控，其余居住于：",
          "2022年4月17日，崇明区新增9例新冠肺炎本土确诊病例、43例本土无症状感染者。除4例途经崇明人员（高速）外，其余病例之前均已落实管控并对居住场所采取封控措施，同时已落实终末消毒等措施。",
          "2022年4月10日，崇明区无新增本土确诊病例，新增55例新冠肺炎无症状感染者，分别居住于：",
          "2022年3月30日，松江区新增8例确诊病例、238例本土无症状感染者，分别居住于：",
          "2022年3月21日，黄浦区无新增本土确诊病例、49例本土无症状感染者，分别居住于：",
          "3月21日，嘉定区新增5例本土确诊病例、98例无症状感染者，分别居住于",
          "2022年3月21日，金山区新增1例本土确诊病例、15例本土无症状感染者。",
          "2022年3月21日（0-24时），普陀区新增1例本土确诊病例、30例本土无症状感染者，分别居住于："
          ]

    for s in ss:
        print(s)
        print(extract_cases(s))
