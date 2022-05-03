from crawler import crawl, get_urls_crawled, save_urls_crawled
from parser import generate_json_files
from overview_parser import generate_overview_json_files
from figture import generate_figtures
from readme import generate_readme_file


if __name__ == '__main__':

    # Crawl the web pages
    pages = ['']
    urls_crawled = get_urls_crawled()
    urls = crawl(pages, urls_crawled)
    len_urls = len(urls)

    urls.extend(urls_crawled)
    save_urls_crawled(urls)

    # Parse htmls to json
    generate_json_files(urls)
    generate_overview_json_files(urls)

    # Gernerate figtures and documents
    generate_figtures()
    generate_readme_file()
