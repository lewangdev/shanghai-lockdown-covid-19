from bs4 import BeautifulSoup


def parse(filename: str):
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
    filename = "archived_html/b080cb3f7031aa0a59313e891e13c38c.html"
    lines = parse(filename)

    print("\n".join(lines))
