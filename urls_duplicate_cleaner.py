import re

# -------------------- CONSTANTS -------------------- #
INPUT_FILE = 'immo_urls.txt'
OUTPUT_FILE = 'immo_urls_no_duplicates.txt'

# -------------------- FUNCTIONS -------------------- #
def retrieve_urls():
    """
    Reads all URLs from the input file.
    Returns:
        List of URLs.
    """
    with open(INPUT_FILE, 'r') as file:
        return file.readlines()


def extract_unique_codes(urls):
    """
    Extracts unique property codes from the list of URLs.
    Args:
        urls (list): List of URLs.
    Returns:
        Set of unique property codes.
    """
    unique_codes = set()
    for url in urls:
        # Remove the base URL and trailing slash/newline
        cleaned_url = re.sub(r'https://www\.immobiliare\.it/annunci/', '', url)
        cleaned_url = re.sub(r'/\n', '', cleaned_url)
        unique_codes.add(cleaned_url)
    return unique_codes


def write_cleaned_urls(unique_codes):
    """
    Writes the cleaned list of unique URLs to the output file.
    Args:
        unique_codes (set): Set of unique property codes.
    """
    with open(OUTPUT_FILE, 'w') as file:
        for code in unique_codes:
            file.write(f'https://www.immobiliare.it/annunci/{code}/\n')
    print(f'File successfully created: {OUTPUT_FILE}')


def clean_url_duplicates():
    """
    Main function to remove duplicate URLs from the input file
    and write a cleaned file with unique URLs.
    """
    urls = retrieve_urls()
    unique_codes = extract_unique_codes(urls)
    write_cleaned_urls(unique_codes)


# -------------------- ENTRY POINT -------------------- #
if __name__ == '__main__':
    clean_url_duplicates()
