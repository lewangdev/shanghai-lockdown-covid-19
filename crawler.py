import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from util import read_file, write_file

archived_html_dir = 'archived_html'
urls_crawled_filename = f"{archived_html_dir}/urls.json"


def get_html_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    return r.text


def get_urls_crawled():
    if os.path.exists(urls_crawled_filename):
        return json.loads(read_file(urls_crawled_filename))

    return []


def save_urls_crawled(urls):
    write_file(json.dumps(urls, ensure_ascii=False, indent=4,
               separators=(',', ':')), urls_crawled_filename)


def crawl(pages, urls_crawled):
    urls = []
    for p in pages:
        url = f"https://wsjkw.sh.gov.cn/yqtb/index{p}.html"

        html_content = get_html_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')

        hyperlink_elements = soup.select('.list-date li')
        for hyperlink_element in hyperlink_elements:
            hyperlink_text = hyperlink_element.text
            hyperlink_url = hyperlink_element.a['href']

            target_url = hyperlink_url
            if not target_url.startswith("http"):
                target_url = 'https://wsjkw.sh.gov.cn' + hyperlink_url

            if target_url in set(map(lambda x: x['url'], urls_crawled)):
                continue

            hyperlink_html_content = get_html_content(target_url)
            hashname = hashlib.md5(
                hyperlink_html_content.encode('utf8')).hexdigest()
            filename = f"{hashname}.html"
            urls.append(
                {"url": target_url, "text": hyperlink_text, "filename": filename})

            write_file(hyperlink_html_content,
                       f"{archived_html_dir}/{filename}")
    return urls


def crawl_url(target_url, text):
    urls = []
    hyperlink_html_content = get_html_content(target_url)
    hashname = hashlib.md5(
        hyperlink_html_content.encode('utf8')).hexdigest()
    filename = f"{hashname}.html"
    urls.append(
        {"url": target_url, "text": text, "filename": filename})

    write_file(hyperlink_html_content,
               f"{archived_html_dir}/{filename}")
    return urls


if __name__ == '__main__':
    # pages = ['', "_1", "_2", "_3", "_4", "_5", "_6"]
    # pages = ['']
    # urls_crawled = get_urls_crawled()
    # urls = crawl(pages, urls_crawled)
    # urls.extend(urls_crawled)
    # save_urls_crawled(urls)
    url = "https://mp.weixin.qq.com/s/zH8lKAD_P6ykUzNLfrrtQg"
    text = "4月26日（0-24时）上海新增1606例本土新冠肺炎确诊病例，新增11956例本土无症状感染者"
    urls_crawled = get_urls_crawled()
    urls = crawl_url(url, text)
    urls.extend(urls_crawled)
    save_urls_crawled(urls)
