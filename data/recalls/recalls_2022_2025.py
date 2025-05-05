import requests
from bs4 import BeautifulSoup
import time
import csv

def scrape_recalled(start_year, end_year):
    """
    Scrapes recalled data from a dictionary with urls and and their years.

    Args:
        start_year (int): Start year
        end_year (int): End year
    
    Returns:
        dict: Dictionary containing the scraped data.
    """
    recalls_data = []

    years = {2022: "https://web.pharmacyboardkenya.org/products-recalled-in-2022/",
             2023: "https://web.pharmacyboardkenya.org/product-recall-2023/",
             2024: "https://web.pharmacyboardkenya.org/Product%20recalled%202024/",
             2025: "https://web.pharmacyboardkenya.org/products-recalled-2025/"}
    for year in range(start_year, end_year + 1):
        url = years.get(year)
        if not url:
            print(f"No URL found for year {year}")
            continue
        print(f"Scraping data from: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            recall_data = []

            # "ecalled products table
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip the header row
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) >= 3:  # Assuming at least Date, Title, Product Type
                        date = columns[1].get_text(strip=True)
                        recall_ref = columns[2].get_text(strip=True) if len(columns) > 2 else None
                        product_column = columns[3]
                        product_link = product_column.find('a')
                        product_text = product_link.get_text(strip=True) if product_link else product_column.get_text(strip=True)
                        inn_name = columns[4].get_text(strip=True) if len(columns) > 4 else None
                        batch_no = columns[5].get_text(strip=True) if len(columns) > 5 else None
                        manufacturer = columns[6].get_text(strip=True) if len(columns) > 6 else None
                        reason = columns[7].get_text(strip=True) if len(columns) > 7 else None
                        status = columns[8].get_text(strip=True) if len(columns) > 8 else None

                        recall_data.append({
                            'year': year,
                            'date': date,
                            'recall_ref': recall_ref,
                            'product_name': product_text,
                            'inn_name': inn_name,
                            'batch_no': batch_no,
                            'manufacturer': manufacturer,
                            'reason': reason
                        })
            recalls_data.extend(recall_data)
            time.sleep(1)# server time delay
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the web page for {year}: {e}")

    return {'recalls': recalls_data}

def save_to_csv(data, filename="recalls_2022_2025.csv"):
    """
    Saves the scraped data to a CSV file.
    
    Args:
        data (dict): Dictionary containing the scraped data.
        filename (str): Name of the CSV file to save the data.
    """
    if not data or not data['recalls']:
        print("No data to save to CSV.")
        return

    fieldnames = data['recalls'][0].keys()
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data['recalls'])
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    start_year = 2022
    end_year = 2025
    scraped_data = scrape_recalled(start_year, end_year)

    if scraped_data:
        save_to_csv(scraped_data)