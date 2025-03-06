from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3
import time
import requests
import os
from dotenv import load_dotenv

# Setup Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run in background
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Retrieve API Key
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Initialize SQLite Database
DB_NAME = "subway_outlets.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS outlets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        address TEXT,
                        operating_hours TEXT,
                        waze_link TEXT,
                        latitude REAL,
                        longitude REAL)''')
    conn.commit()
    conn.close()

# Geocoding Function (Using OpenStreetMap API)
def get_geocode(address):
    base_url = f"https://maps.googleapis.com/maps/api/geocode/json?"
    params = {
        "key": GOOGLE_MAPS_API_KEY,
        "address": address,
    }
    response = requests.get(base_url, params=params).json()
    response.keys()

    if response["status"] == "OK":
        geometry = response["results"][0]["geometry"]
        lat = geometry["location"]["lat"]
        lon = geometry["location"]["lng"]
        
        return lat, lon
    
    return None, None

# Scrape and Store Outlets
def scrape_and_store():

    # Open Subway Find-a-Store page
    URL = "https://subway.com.my/find-a-subway"
    driver.get(URL)
    time.sleep(3)  # Allow page to load

    # Filter by kuala lumpur
    search_box = driver.find_element(By.ID, "fp_searchAddress")  # Adjust if ID is different
    search_box.clear()
    search_box.send_keys("kuala lumpur")
    search_box.send_keys(Keys.RETURN)

    WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "fp_ll_holder"))
    )
    # time.sleep(5)  # Allow results to load

    # Connect to SQLite database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get outlet list
    outlets = driver.find_elements(By.CLASS_NAME, "fp_listitem")

    for outlet in outlets:

        # Check if the outlet is visible
        if outlet.value_of_css_property("display") == "none":
            continue  # Skip hidden elements

        # Extract name
        try:
            name = outlet.find_element(By.TAG_NAME, "h4").text
        except:
            name = "Unknown"

        # Extract details
        details = outlet.text.split("\n")
        address = details[1] if len(details) > 1 else "Unknown"
        operating_hours = details[2] if len(details) > 2 else "Unknown"

        # Extract Waze link
        try:
            waze_link = outlet.find_element(By.XPATH, './/a[contains(@href, "waze.com")]').get_attribute("href")
        except:
            waze_link = "Not Found"

        # Get Geolocation
        lat, lon = get_geocode(address)

        # Save to database
        cursor.execute("""
            INSERT INTO outlets (name, address, operating_hours, waze_link, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, address, operating_hours, waze_link, lat, lon))

        print(f"Added: {name}, {address}, {operating_hours}, {waze_link}, ({lat}, {lon})")

    conn.commit()
    conn.close()


init_db()
scrape_and_store()

driver.quit()
