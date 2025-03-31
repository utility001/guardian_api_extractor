import os
import logging
from dotenv import load_dotenv

from guardian_utils import (
    from_guardian_api, get_current_page_no, get_total_pages,
    get_total_results, get_articles, to_csv_file
)

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} - {levelname} - {message}",
    style="{", datefmt="%Y-%m-%d %H:%M:%S")

load_dotenv()

SEARCH_TERM = "Nigeria"
FROM_DATE = "2024-01-01"
TO_DATE = "2025-01-01"
FILENAME = "mydata"
PAGE_SIZE = 20
API_KEY = os.getenv("API_KEY") # API KEY HERE

# Make the first request, It contains some needed metadata
from_api = from_guardian_api(search_term=SEARCH_TERM, api_key=API_KEY,
                             from_date=FROM_DATE, to_date=TO_DATE,
                             page=1, page_size=PAGE_SIZE, show_fields='body')

# metadata
total_results = get_total_results(from_api)
total_pages = get_total_pages(from_api)
current_page_no = get_current_page_no(from_api)

# Helpful information to for logging
if current_page_no == 1:
    logging.info(f'FOUND {total_results} results in TOTAL')

# extract and save first page articles
articles = get_articles(from_api)
to_csv_file(filename=FILENAME, input=articles)


# Now iterate through the rest of the pages by updating page number
for page_no in range(current_page_no+1, total_pages+1):
    from_api = from_guardian_api(
        search_term=SEARCH_TERM, api_key=API_KEY,
        from_date=FROM_DATE, to_date=TO_DATE,
        page=page_no, page_size=PAGE_SIZE, show_fields='body'
        )
    
    articles = get_articles(from_api)
    to_csv_file(filename=FILENAME, input=articles)

