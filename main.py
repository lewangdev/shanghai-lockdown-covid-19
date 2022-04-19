import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup, SoupStrainer


def get_html(url):
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

    urls = {}
    if os.path.exists(url_filename):
        urls = json.loads(read_file(url_filename))

    pages = ['', '_1', "_2", "_3", "_4", "_5"]
    for p in pages:
        url = 'https://wsjkw.sh.gov.cn/yqtb/index%s.html' % p

        if url in set(urls.keys()):
            continue

        html_doc = get_html(url)
        soup = BeautifulSoup(html_doc, 'html.parser')

        link_elements = soup.select('.list-date li')
        for link_element in link_elements:
            link_text = link_element.text
            link_url = link_element.a['href']

            target_url = link_url
            if not target_url.startswith("http"):
                target_url = 'https://wsjkw.sh.gov.cn' + link_url

            link_html_content = get_html(target_url)
            filename = "%s.html" % hashlib.md5(
                link_html_content.encode('utf8')).hexdigest()
            urls[target_url] = {"text": link_text, "filename": filename}

            write_file(link_html_content, "archived_html/" +
                       filename)

    write_file(json.dumps(urls, ensure_ascii=False, indent=4,
               separators=(',', ':')), url_filename)
