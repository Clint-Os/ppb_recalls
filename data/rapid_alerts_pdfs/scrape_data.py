import requests
from bs4 import BeautifulSoup
import time
import csv

def scrape_rapid_alerts(base_url_prefix, start_year, end_year):
    """
    Scrapes rapid alerts data from a range of years.

    Args:
        base_url_prefix (str): https://web.pharmacyboardkenya.org/
        start_year (int): i.e. 2018
        end_year (int): i.e. 2025
    
    Returns:
        dict: Dictionary containing the scraped data.
    """
    all_alerts_data = []
    for year in range(start_year, end_year + 1):
        if 2021 <= year <= 2024:
            url = f"{base_url_prefix}rapid-alert-{year}/"
        else:
            url = f"{base_url_prefix}rapid-alerts-{year}/"
        print(f"Scraping data from: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            rapid_alerts_data = []

            # "rapid-alerts-table"
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip the header row
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) >= 3:  # Assuming at least Date, Title, Product Type
                        date = columns[1].get_text(strip=True)
                        title_column = columns[2]
                        title_link = title_column.find('a')
                        title_text = title_link.get_text(strip=True) if title_link else title_column.get_text(strip=True)
                        pdf_url = title_link['href'] if title_link and 'href' in title_link.attrs else None
                        product_type = columns[3].get_text(strip=True) if len(columns) > 3 else None
                        source = columns[4].get_text(strip=True) if len(columns) > 4 else None
                        manufacturer = columns[5].get_text(strip=True) if len(columns) > 5 else None

                        rapid_alerts_data.append({
                            'year': year,
                            'date': date,
                            'title': title_text,
                            'pdf_url': pdf_url,
                            'product_type': product_type,
                            'source': source,
                            'manufacturer': manufacturer
                        })
            all_alerts_data.extend(rapid_alerts_data)
            time.sleep(1) # Be respectful to the server by adding a small delay

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the web page for {year}: {e}")

    return {'rapid_alerts': all_alerts_data}

def save_to_csv(data, filename="rapid_alerts.csv"):
    """
    Saves the scraped data to a CSV file.
    
    Args:
        data (dict): Dictionary containing the scraped data.
        filename (str): Name of the CSV file to save the data.
    """
    if not data or not data['rapid_alerts']:
        print("No data to save to CSV.")
        return

    fieldnames = data['rapid_alerts'][0].keys()
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data['rapid_alerts'])
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

if __name__ == "__main__":
    base_url_prefix = "https://web.pharmacyboardkenya.org/"
    start_year = 2018
    end_year = 2025
    scraped_data = scrape_rapid_alerts(base_url_prefix, start_year, end_year)

    if scraped_data:
        save_to_csv(scraped_data)