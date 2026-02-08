import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def download_file(url, target_path):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if os.path.exists(target_path):
        logging.info(f"Skipping download, file exists: {target_path}")
        return
    logging.info(f"Downloading {url} to {target_path}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(target_path, 'wb') as f:
        f.write(response.content)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, 'data/raw')
    os.makedirs(raw_dir, exist_ok=True)
    
    # Diabetes Dataset
    download_file("https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv", os.path.join(raw_dir, "diabetes_raw.csv"))

if __name__ == "__main__":
    main()
