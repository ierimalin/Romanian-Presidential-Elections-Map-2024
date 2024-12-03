import os
import requests
import time
import subprocess

datadir = "data/raw"
csvfile = f"{datadir}/election_data.csv"
csv_url = "https://prezenta.roaep.ro/parlamentare01122024/data/csv/sicpv/pv_part_cntry_s.csv"

import time

def download_election_data():
    start_time = time.time()
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
        print(f"Time taken to download: {time.time() - start_time} seconds")
    except requests.RequestException as e:
        print(f"Error: {e}")

def run_process_data():
    start_time = time.time()
    try:
        print("Processing the downloaded election data...")
        result = subprocess.run(['python', os.path.join("scripts", 'process_data.py')], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Processing complete.")
            print("Output:", result.stdout)
        else:
            print(f"Error running process_data.py: {result.stderr}")
        print(f"Time taken to process: {time.time() - start_time} seconds")
    except Exception as e:
        print(f"Error running process_data.py: {e}")


        
def automate_data_fetching():
    while True:
        download_election_data()
        run_process_data()
        time.sleep(100)

if __name__ == "__main__":
    automate_data_fetching()
    
    
    



