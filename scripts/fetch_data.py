import requests
import os

def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(target_path, 'wb') as f:
        f.write(response.content)
    print("Done.")

def main():
    raw_data_dir = 'data/raw'
    os.makedirs(raw_data_dir, exist_ok=True)

    # UCI Heart Disease Dataset (Cleveland)
    # The processed.cleveland.data file is a common starting point
    heart_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
    download_file(heart_url, os.path.join(raw_data_dir, "heart_disease_raw.csv"))

    # Pima Indians Diabetes Dataset
    # Using a reliable mirror since the original UCI link can be tricky sometimes
    diabetes_url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    download_file(diabetes_url, os.path.join(raw_data_dir, "diabetes_raw.csv"))

if __name__ == "__main__":
    main()
