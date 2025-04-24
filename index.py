from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import json
import os

app = Flask(__name__)

# URL of the webpage to scrape
URL = "https://rtu.sumsraj.com/main.aspx"  # Replace with the actual URL

# Path to the JSON file to store previously fetched news items
FILE_PATH = "btech_result_news.json"

# Function to load existing news data from file
def load_existing_news(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

# Function to save news data to file
def save_news(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to scrape news from the webpage
def scrape_news(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.select("ul.News li")
        return [item.text.strip() for item in news_items if ("B-TECH" in item.text.upper() or "B.TECH" in item.text.upper()) and "RESULT" in item.text.upper()]
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

# Function to compare and detect new news items
def detect_new_news(existing_news, latest_news):
    return [news for news in latest_news if news not in existing_news]

@app.route('/scrape-news', methods=['GET'])
def trigger_scraping():
    # Load existing news from file
    existing_news = load_existing_news(FILE_PATH)
    
    # Scrape the latest news
    latest_news = scrape_news(URL)
    
    # Detect new news items
    new_news = detect_new_news(existing_news, latest_news)
    
    if new_news:
        print("New B.Tech Result Related News Found:")
        for news in new_news:
            print(news)
        
        save_news(FILE_PATH, existing_news + new_news)
        
        ACTION_URL = "https://smartlinksoft.in/test1.php"
        for news in new_news:
            response = requests.post(ACTION_URL, data={'msg': news})
            if response.status_code == 200:
                print("Notification sent successfully.")
            else:
                print(f"Failed to send notification. Status code: {response.status_code}")

        return jsonify({"status": "success", "new_news": new_news}), 200
    else:
        return jsonify({"status": "success", "message": "No new B.Tech Result related news."}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Change the port as needed
