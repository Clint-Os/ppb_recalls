import requests
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
from urllib.parse import urljoin

csv_filepath = "product_info.csv"

def get_url(csv_filepath):
    """
    Read product info URLs from product_info.csv 

    Args:
        csv_filepath (str)
    """
    url_list = []
    try:
        df = pd.read_csv(csv_filepath)
        for index, row in df.iterrows():
            year = row['year']
            product_url = row['url']
            if pd.notna(product_url):  # Check for non-missing URLs
                print(f"Processing URL from CSV: {product_url}")
                url_list.append({
                    'year': year,
                    'url': product_url
                })
            else:
                print(f"Warning: Skipping row at index {index} with empty 'url'.")
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_filepath}")
    except Exception as e:  
        print(f"An error occurred while processing the CSV file: {e}")
    return url_list


def download_pdfs(url_list, download_folder):
    """
    Downloads all PDF files found on the URLs in the provided list.

    Args:
        url_list (list): A list of dictionaries, where each dictionary contains
                         'url' (the URL to scrape) and 'year'.
        download_folder (str): The folder to save the downloaded PDFs.
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for item in url_list:
        url = item['url']
        year = item['year']
        print(f"Scraping data from: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

            soup = BeautifulSoup(response.content, 'html.parser')
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.lower().endswith('.pdf'):
                    pdf_links.append(urljoin(url, href))  # Make sure the URL is absolute

            for pdf_url in pdf_links:
                try:
                    print(f"Downloading PDF: {pdf_url}")
                    pdf_response = requests.get(pdf_url, stream=True)
                    pdf_response.raise_for_status()

                    filename = os.path.join(download_folder, f"{year}_{os.path.basename(pdf_url)}")
                    with open(filename, 'wb') as pdf_file:
                        for chunk in pdf_response.iter_content(chunk_size=8192):
                            pdf_file.write(chunk)
                    print(f"Saved PDF to: {filename}")
                    time.sleep(1)  # Be polite and add a delay

                except requests.exceptions.RequestException as e:
                    print(f"Error downloading {pdf_url}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred while processing {pdf_url}: {e}")

            time.sleep(2)  # Add a delay between processing different URLs

        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {url}: {e}")

if __name__ == "__main__":
    download_folder = "downloaded_pdfs"
    url_list = get_url(csv_filepath)
    if url_list:  # Only proceed if URLs were successfully retrieved
        download_pdfs(url_list, download_folder)
    else:
        print("No URLs found in the CSV file. Exiting.")