import requests
from bs4 import BeautifulSoup
import os
import time

def extract_pdf_links_and_titles(base_url_prefix, start_year, end_year):
    """
    Scrapes web pages for a range of years and extracts PDF links and their titles from tables.

    Args:
        base_url_prefix (str): The base URL of the website (e.g., "https://web.pharmacyboardkenya.org/").
        start_year (int): The starting year for scraping.
        end_year (int): The ending year for scraping.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'title' and 'url' of a PDF.
    """
    pdf_info = []
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

            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # Skip the header row
                for row in rows:
                    columns = row.find_all('td')
                    if len(columns) >= 3:
                        title_column = columns[2]
                        title_link = title_column.find('a', href=True)
                        if title_link and title_link['href'].endswith('.pdf'):
                            pdf_url = title_link['href']
                            title_text = title_link.get_text(strip=True)
                            pdf_info.append({'title': title_text, 'url': pdf_url})
            else:
                print(f"No table found on {url}")
            time.sleep(1)  # Be respectful to the server

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the web page {url}: {e}")
    return pdf_info

def download_pdfs(pdf_info_list, download_folder="rapid_alerts_pdfs"):
    """
    Downloads PDF files from a list of dictionaries containing titles and URLs.

    Args:
        pdf_info_list (list): A list of dictionaries with 'title' and 'url' keys.
        download_folder (str, optional): The folder to save the downloaded PDFs.
            Defaults to "rapid_alerts_pdfs".
    """
    # Create output directory if it doesn't exist
    os.makedirs(download_folder, exist_ok=True)

    # Download each PDF
    for info in pdf_info_list:
        try:
            # Create a safe filename from the title
            safe_filename = ''.join(c for c in info['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = os.path.join(download_folder, f"{safe_filename}.pdf")

            # Download and save the PDF
            print(f"Downloading {info['url']} as {filename}")
            response = requests.get(info['url'], stream=True)
            response.raise_for_status()

            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Downloaded: {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {info['url']}: {e}")
        except IOError as e:
            print(f"Error saving file {filename}: {e}")

if __name__ == "__main__":
    base_url_prefix = "https://web.pharmacyboardkenya.org/"
    start_year = 2018
    end_year = 2025
    pdf_links = extract_pdf_links_and_titles(base_url_prefix, start_year, end_year)
    download_pdfs(pdf_links)
    print("Finished downloading PDFs.")