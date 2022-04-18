import requests
from bs4 import BeautifulSoup, SoupStrainer


def get_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    return r.text


def write_html(html, filename):
    with open(filename, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    pages = ['']
    for p in pages:
        url = 'https://wsjkw.sh.gov.cn/yqtb/index%s.html' % p
        html_doc = get_html(url)
        soup = BeautifulSoup(html_doc, 'html.parser')

        link_elements = soup.select('.list-date li')
        for link_element in link_elements:
            link_text = link_element.text
            link_url = link_element.a['href']

            target_url = link_url
            if not target_url.startswith("http"):
                target_url = 'https://wsjkw.sh.gov.cn' + link_url
            link_html_doc = get_html(target_url)
            write_html(link_html_doc, "archived_html/" +
                       link_url.replace("/", "_"))
