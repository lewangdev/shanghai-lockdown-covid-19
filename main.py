from crawler import crawl, get_urls_crawled, save_urls_crawled
from parser import generate_json_files
from overview_parser import generate_overview_json_files
from figture import generate_figtures
from readme import generate_readme_file
from util import get_data
from poi import generate_places
from db import create_db_files


if __name__ == '__main__':

    # Crawl the web pages
    pages = ['']
    urls_crawled = get_urls_crawled()
    urls = crawl(pages, urls_crawled)
    len_urls = len(urls)

    urls.extend(urls_crawled)
    save_urls_crawled(urls)

    # Parse htmls to json
    json_filenames = generate_json_files(urls[0:len_urls])
    generate_overview_json_files(urls[0:len_urls])
    # generate_json_files(urls)
    # generate_overview_json_files(urls)

    # Gernerate figtures and documents
    generate_figtures()
    generate_readme_file()

    # Generate places
    cases = get_data(json_filenames)
    generate_places(cases)

    # Create db files when new urls crawled
    # if len_urls > 0:
    #    create_db_files()
