import requests
from bs4 import BeautifulSoup
import time
import csv

def scrape_recalled(base_url_prefix, start_year, end_year):
    """
    Scrapes recalled data from a range of years.

    Args:
        base_url_prefix (str): https://web.pharmacyboardkenya.org/
        start_year (int): i.e. 2016
        end_year (int): i.e. 2021
    
    Returns:
        dict: Dictionary containing the scraped data.
    """
    all_alerts_data = []
    for year in range(start_year, end_year + 1):
        url = f"{base_url_prefix}products-recalled-in-{year}/"
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
                        product_name = columns[2].get_text(strip=True) if len(columns) > 2 else None
                        inn_name = columns[3].get_text(strip=True) if len(columns) > 3 else None
                        batch_no = columns[4].get_text(strip=True) if len(columns) > 4 else None
                        manufacturer = columns[5].get_text(strip=True) if len(columns) > 5 else None
                        reason = columns[6].get_text(strip=True) if len(columns) > 6 else None

                        recall_data.append({
                            'year': year,
                            'date': date,
                            'product_name': product_name,
                            'inn_name': inn_name,
                            'batch_no': batch_no,
                            'manufacturer': manufacturer,
                            'reason': reason
                        })
            all_alerts_data.extend(recall_data)
            time.sleep(1)# server time delay
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the web page for {year}: {e}")

    return {'recalls': all_alerts_data}

def save_to_csv(data, filename="recalls_2016_2021.csv"):
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
    base_url_prefix = "https://web.pharmacyboardkenya.org/"
    start_year = 2016
    end_year = 2021
    scraped_data = scrape_recalled(base_url_prefix, start_year, end_year)

    if scraped_data:
        save_to_csv(scraped_data)