import os
import requests
import time

datadir = "data/raw"
csvfile = f"{datadir}/election_data.csv"
csv_url = "https://prezenta.roaep.ro/parlamentare01122024/data/csv/sicpv/pv_part_cntry_s.csv"

def download_election_data():
    os.makedirs(datadir, exist_ok=True)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(csv_url, headers=headers, timeout=30)
        response.raise_for_status()
        with open(csvfile, "wb") as file:
            file.write(response.content)
        print(f"Data fetched; saved to {csvfile}")
    
    except requests.RequestException as e:
        print(f"Error: {e}")
        
        
def automate_data_fetching():
    while True:
        download_election_data()
        time.sleep(300)

if __name__ == "__main__":
    automate_data_fetching()

