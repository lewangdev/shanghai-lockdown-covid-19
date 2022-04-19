import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup, SoupStrainer


def get_html_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    return r.text


def write_file(content, filename):
    with open(filename, 'w') as f:
        f.write(content)


def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()


if __name__ == '__main__':

    url_filename = 'archived_html/urls.json'

    urls = []
    if os.path.exists(url_filename):
        urls = json.loads(read_file(url_filename))

    pages = ['']
    for p in pages:
        url = 'https://wsjkw.sh.gov.cn/yqtb/index%s.html' % p

        html_content = get_html_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        hyperlink_elements = soup.select('.list-date li')
        for hyperlink_element in hyperlink_elements:
            hyperlink_text = hyperlink_element.text
            hyperlink_url = hyperlink_element.a['href']

            target_url = hyperlink_url
            if not target_url.startswith("http"):
                target_url = 'https://wsjkw.sh.gov.cn' + hyperlink_url

            if target_url in set(map(lambda x: x['url'], urls)):
                continue

            hyperlink_html_content = get_html_content(target_url)
            filename = "%s.html" % hashlib.md5(
                hyperlink_html_content.encode('utf8')).hexdigest()
            urls.insert(
                0, {"url": target_url, "text": hyperlink_text, "filename": filename})

            write_file(hyperlink_html_content, "archived_html/" +
                       filename)

    write_file(json.dumps(urls, ensure_ascii=False, indent=4,
               separators=(',', ':')), url_filename)
