import requests
from bs4 import BeautifulSoup
import json
import re

# -------------------- CONSTANTS -------------------- #
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
CHECKPOINT_FILE = 'urls_and_dataset_checkpoints.txt'
URLS_FILE = 'immo_urls_no_duplicates.txt'
DATASET_FILE = 'dataset.json'


# -------------------- CHECKPOINT FUNCTIONS -------------------- #
def continue_from_checkpoint():
    """
    Reads the number of houses already saved from the checkpoint file.
    Returns:
        int: Number of houses saved so far.
    """
    with open(CHECKPOINT_FILE, 'r') as file:
        return int(file.readlines()[1].strip())


def update_checkpoint(houses_saved):
    """
    Updates the checkpoint file with the current number of houses saved.
    Args:
        houses_saved (int): Total number of houses saved.
    """
    with open(CHECKPOINT_FILE, 'r') as file:
        lines = file.readlines()
    lines[1] = f'{houses_saved}\n'
    with open(CHECKPOINT_FILE, 'w') as file:
        file.writelines(lines)


# -------------------- DATA EXTRACTION FUNCTIONS -------------------- #
def get_urls(houses_saved):
    """
    Retrieves house URLs starting from a specific index.
    Args:
        houses_saved (int): Index to start retrieving URLs.
    Returns:
        list: List of house URLs.
    """
    with open(URLS_FILE, 'r') as file:
        urls = [url.strip() for url in file.readlines()]
    return urls[houses_saved:]


def get_house_info(url, errors):
    """
    Fetches and parses house information from a given URL.
    Args:
        url (str): URL of the house listing.
        errors (int): Current count of errors.
    Returns:
        dict: Dictionary of house details.
        int: Updated error count.
    """
    try:
        response = requests.get(url, HEADERS)
        if response.status_code == 200:
            page_info = BeautifulSoup(response.text, 'html.parser')
            titles = [dt.get_text(strip=True) for dt in page_info.find_all('dt', class_='re-featuresItem__title')]
            characteristics = [dd.get_text(strip=True) for dd in
                               page_info.find_all('dd', class_='re-featuresItem__description')]
            return dict(zip(titles, characteristics)), errors
        else:
            print(f'Error {response.status_code}: Failed to fetch data from {url}.')
    except Exception as e:
        print(f'Exception occurred while processing {url}: {e}')

    errors += 1
    return {}, errors


def save_data(house_info):
    """
    Appends house information to the dataset file.
    Args:
        house_info (dict): Dictionary containing house details.
    """
    with open(DATASET_FILE, 'a', encoding='utf-8') as file:
        json.dump(house_info, file, ensure_ascii=False, indent=4)
        file.write(",\n")


# -------------------- MAIN FUNCTION -------------------- #
def create_dataset():
    """
    Main function to create the dataset by fetching house details
    and updating checkpoints incrementally.
    """
    errors = 0
    houses_saved = continue_from_checkpoint()
    urls = get_urls(houses_saved)

    print(f'Starting dataset creation from house {houses_saved + 1}. Total URLs to process: {len(urls)}.')

    for index, url in enumerate(urls, start=1):
        house_info, errors = get_house_info(url, errors)

        if house_info:  # Save only if house information was successfully retrieved
            save_data(house_info)
            houses_saved += 1
            update_checkpoint(houses_saved)
            print(f'[{houses_saved}] Saved data for URL: {url}')
        else:
            print(f'Skipped URL due to error.')

    print(f'\nDataset successfully created. Total houses saved: {houses_saved}. Errors encountered: {errors}.')


# -------------------- ENTRY POINT -------------------- #
if __name__ == '__main__':
    create_dataset()
