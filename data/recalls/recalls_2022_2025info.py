import requests
from bs4 import BeautifulSoup
import csv
import time

def extract_product_info(start_year, end_year):
    """
    Scrapes web pages for a range of years and extracts Product info.

    Args:
        start_year (int): The starting year for scraping.
        end_year (int): The ending year for scraping.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'title' and 'url' of a Product info.
    """
    product_info = []

    years = {2022: "https://web.pharmacyboardkenya.org/products-recalled-in-2022/",
             2023: "https://web.pharmacyboardkenya.org/product-recall-2023/",
             2024: "https://web.pharmacyboardkenya.org/Product%20recalled%202024/",
             2025: "https://web.pharmacyboardkenya.org/products-recalled-2025/"
             }

    for year in range(start_year, end_year + 1):
        url = years.get(year)
        if not url:
            print(f"No URL found for year {year}")
            continue
        print(f"Scraping data from: {url}")
        time.sleep(1)  # Be respectful to the server

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip the header row
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) >= 3:
                        product_column = columns[3]
                        product_link = product_column.find('a', href=True)  # Find the link
                        product_text = product_link.get_text(strip=True) if product_link else product_column.get_text(strip=True)
                        product_url = product_link['href'] if product_link and 'href' in product_link.attrs else None

                        product_info.append({
                            'year': year,
                            'product': product_text,
                            'url': product_url
                        })
            else:
                print(f"No product info found for {url}")
            time.sleep(1)  # Be respectful to the server

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the web page {url}: {e}")

    return {'product_info': product_info}

def save_to_csv(data, filename="product_info.csv"):
    """
    Saves the scraped data to a CSV file.
    
    Args:
        data (dict): Dictionary containing the scraped data.
        filename (str): Name of the CSV file to save the data.
    """
    if not data or not data['product_info']:
        print("No data to save to CSV.")
        return

    fieldnames = data['product_info'][0].keys()
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data['product_info'])
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


if __name__ == "__main__":
    start_year = 2022
    end_year = 2025
    product_info = extract_product_info(start_year, end_year)
    save_to_csv(product_info)