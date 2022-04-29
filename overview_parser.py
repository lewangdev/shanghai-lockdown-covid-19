import re
import json
from bs4 import BeautifulSoup
from crawler import get_urls_crawled


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
    # '市卫健委今早（28日）通报：2022年4月27日0—24时，新增本土新冠肺炎确诊病例1292（含既往无症状感染者转为确诊病例858例）和无症状感染者9330例，432例确诊病例和9140例无症状感染者在隔离管控中发现，其余在相关风险人群排查中发现。无新增境外输入性新冠肺炎确诊病例和无症状感染者。'
    found = False
    regex1 = ".*市卫健委(.*?)通报：(.*?)(\\d+)年(\\d+)月(\\d+)日(.*?)新增本土新冠肺炎确诊病例(\\d+)(.*?)和无症状感染者(\\d+)例.*?"
    m1 = re.match(regex1, line, re.IGNORECASE)
    if not found and m1 is not None:
        (_, _, y, m, d, _, confirmed, _, asymptomatic) = m1.groups()
        found = True
        return found, dict(
            date=f"{y}-{m:0>2}-{d:0>2}", confirmed=int(confirmed), asymptomatic=int(asymptomatic),
            total=int(confirmed)+int(asymptomatic), asymptomatic_to_confirmed=0
        )

    regex2 = "(\\d+)年(\\d+)月(\\d+)日(.*?)新增本土新冠肺炎确诊病例(\\d+)例(.*?)和无症状感染者(\\d+)例.*?"
    m2 = re.match(regex2, line, re.IGNORECASE)
    if not found and m2 is not None:
        (y, m, d, _, confirmed, _, asymptomatic) = m2.groups()
        found = True
        return found, dict(
            date=f"{y}-{m:0>2}-{d:0>2}", confirmed=int(confirmed), asymptomatic=int(asymptomatic),
            total=int(confirmed)+int(asymptomatic), asymptomatic_to_confirmed=0
        )

    return found, {}


def extract_a2c(line: str):
    # 其中5062例确诊病例为既往无症状感染者转归
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


def extract_deaths(line: str):
    regex_deaths = "(.*?)新增本土死亡(\\d+)例.*?"
    deaths = 0
    deaths_match = re.match(regex_deaths, line, re.IGNORECASE)
    if deaths_match is not None:
        (_, deaths) = deaths_match.groups()
        return True, int(deaths)

    return False, 0


def parse_lines_to_json(lines):
    a2c_found = False
    deaths_found = False
    found = False
    a2c = 0
    deaths = 0
    ret = {"deaths": 0, "confirmed": 0,
           "asymptomatic": 0, "asymptomatic_to_confirmed": 0}
    for line in lines:
        if not a2c_found:
            (a2c_found, a2c) = extract_a2c(line)

        if not deaths_found:
            (deaths_found, deaths) = extract_deaths(line)
        if not found:
            (found, ret) = extract_cases(line)
            ret['asymptomatic_to_confirmed'] = a2c
            ret['deaths'] = deaths
        if found and deaths_found and a2c_found:
            ret['total'] = ret['total'] - a2c
            ret['asymptomatic_to_confirmed'] = a2c
            ret['deaths'] = deaths
            return ret

    return ret


def parse_html_to_json(filename: str):
    lines = parse_html_to_lines(filename)
    return parse_lines_to_json(lines)


def generate_overview_json_files(urls):
    regex = "(.*?)月(\\d+)日(.*?)新增(.*?)确诊病例.*?"
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

        if total.get('date') is None:
            print(f"Ignore: {filename}")
            continue

        with open(f"data/overview/{total['date']}.json", 'w') as f:
            f.write(ret)


def test_parse_html():
    filename = "archived_html/221e6e50a84c1a9700e3caedc8982440.html"
    total = parse_html_to_json(filename)
    ret = json.dumps(total, ensure_ascii=False,
                     indent=4, separators=(',', ':'))
    print(ret)


if __name__ == "__main__":
    # test_parse_html()

    urls = get_urls_crawled()
    generate_overview_json_files(urls)
