import requests
from bs4 import BeautifulSoup
import re

# -------------------- CONSTANTS -------------------- #
BASE_URL = 'https://www.immobiliare.it/vendita-case/roma/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
CHECKPOINT_FILE = 'urls_and_dataset_checkpoints.txt'
URLS_FILE = 'immo_urls.txt'

# -------------------- CHECKPOINT FUNCTIONS -------------------- #
def continue_from_checkpoint():
    """
    Reads the checkpoint file to resume scraping from the last price range.
    """
    with open(CHECKPOINT_FILE, 'r') as file:
        line = file.readline().strip()
        min_price, max_price = map(int, line.split())
    return [min_price, max_price]


def update_checkpoint(price_range):
    """
    Updates only the first line of the checkpoint file with the current price range.
    Keeps the second line (house count) untouched.
    """
    with open(CHECKPOINT_FILE, 'r') as file:
        lines = file.readlines()

    # Update only the first line
    lines[0] = f'{price_range[0]} {price_range[1]}\n'

    with open(CHECKPOINT_FILE, 'w') as file:
        file.writelines(lines)


# -------------------- SCRAPING FUNCTIONS -------------------- #
def scrape_every_house_url_in_rome():
    """
    Main function to scrape all house URLs from immobiliare.it for different price ranges.
    """
    price_range = continue_from_checkpoint()
    all_urls = []

    while True:
        price_range_page_url = f'{BASE_URL}?prezzoMinimo={price_range[0]}&prezzoMassimo={price_range[1]}'
        all_pages_urls = scrape_all_pages_for_price_range(price_range_page_url, price_range)
        save_urls(all_pages_urls)
        all_urls += all_pages_urls

        price_range = change_price_range(price_range)
        update_checkpoint(price_range)

        if isinstance(price_range, str):
            print(f'Process finished. A total of {len(all_urls)} URLs have been retrieved.')
            break


def scrape_all_pages_for_price_range(price_range_page_url, price_range):
    """
    Retrieves all page URLs for a given price range.
    """
    all_pages_urls = []
    page = 0

    while True:
        page_url, page = change_page(price_range_page_url, page)
        page_urls, response_status = get_page_urls(page_url, page)
        all_pages_urls.extend(page_urls)

        if response_status == 404:
            print(f'\nTotal pages for the {price_range} price range: {page - 1}.')
            print(f'Total URLs retrieved for this price range: {len(all_pages_urls)}.')
            return all_pages_urls


def get_page_urls(page_url, page):
    """
    Extracts property listing URLs from a specific page.
    """
    response = requests.get(page_url, HEADERS)

    if response.status_code == 200:
        page_info = BeautifulSoup(response.text, 'html.parser')
        if page == 1:
            log_total_urls_to_scrape(page_info)

        page_urls = [
            element['href']
            for element in page_info.find_all('a', class_='in-listingCardTitle')
            if 'asta' not in element.get('title', '')
        ]
        print(f'Page {page}: Successfully retrieved {len(page_urls)} URLs.')
        return page_urls, response.status_code

    log_request_error(response.status_code)
    return [], response.status_code


# -------------------- SUPPORT FUNCTIONS -------------------- #
def log_total_urls_to_scrape(page_info):
    """
    Logs the total number of URLs to scrape for a price range.
    """
    result_text = page_info.find('div', class_='in-realEstateListHeader__title').get_text(strip=True)
    total_urls = re.sub(r' risultati per:case in vendita Roma', '', result_text)
    print(f'Total URLs to scrape in this range: {total_urls}')


def log_request_error(status_code):
    """
    Logs errors based on HTTP status codes.
    """
    if status_code == 403:
        print(f'Access denied: Error {status_code}.')
    elif status_code != 404:
        print(f'Unknown error: {status_code}.')


def change_page(base_url, page):
    """
    Navigates to the next page of listings.
    """
    page += 1
    return f'{base_url}&pag={page}', page


def save_urls(urls):
    """
    Appends URLs to the output file.
    """
    with open(URLS_FILE, 'a') as file:
        for url in urls:
            file.write(f'{url}\n')
    print(f'{len(urls)} URLs successfully saved to {URLS_FILE}.\n')


def change_price_range(price_range):
    """
    Adjusts the price range for filtering listings.
    """
    if price_range[0] < 400_000:
        increments = [20_000, 20_000]
    elif price_range[1] == 420_000:
        price_range = [350_000, 400_000]
        increments = [50_000, 50_000]
    elif price_range[0] < 1_000_000:
        increments = [50_000, 50_000]
    else:
        increments = [0, 3_950_000]
        if price_range[1] >= 5_000_000:
            return 'The available price ranges have finished.'

    return [value + increment for value, increment in zip(price_range, increments)]


# -------------------- ENTRY POINT -------------------- #
if __name__ == '__main__':
    scrape_every_house_url_in_rome()
