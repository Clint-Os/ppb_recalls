import requests
from bs4 import BeautifulSoup

def scrape_rapid_alerts(url):
    """Scrapes rapid alerts data.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        rapid_alerts_data = []

        # --- Adapt this selector based on the actual HTML structure ---
        # Example: If the alerts are in a table with class "rapid-alerts-table"
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
                        'date': date,
                        'title': title_text,
                        'pdf_url': pdf_url,
                        'product_type': product_type,
                        'source': source,
                        'manufacturer': manufacturer
                    })
        return {'rapid_alerts': rapid_alerts_data}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the web page: {e}")
        return None

if __name__ == "__main__":
    target_url = "https://web.pharmacyboardkenya.org/rapid-alerts-2025/"  # Replace with the actual URL
    scraped_data = scrape_rapid_alerts(target_url)

    if scraped_data:
        print("--- Rapid Alerts Data ---")
        for alert in scraped_data['rapid_alerts']:
            print(alert)