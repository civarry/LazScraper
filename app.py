from flask import Flask, render_template, request, send_file
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from io import StringIO

app = Flask(__name__)

def scrape_lazada_products(base_url, num_pages):
    # Initialize the WebDriver
    chrome_options = Options()
    driver_path = 'chromedriver.exe'  # Ensure this points to your correct chromedriver location
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    scraped_data = []

    # Main loop to iterate through pages
    for page_number in range(1, num_pages + 1):
        # Construct the URL for the current page
        url = base_url.format(page_number)
        
        # Navigate to the current page
        driver.get(url)
        
        # Find all product items
        product_items = driver.find_elements(By.CSS_SELECTOR, '[data-qa-locator="product-item"]')
        
        # Check if there are no more product items on the page
        if not product_items:
            print("No more product items found. Exiting loop.")
            break
        
        # Iterate through each product item and extract information
        for item in product_items:
            try:
                # Find elements within each product item and extract the necessary information
                item_name_element = item.find_element(By.CSS_SELECTOR, '.POgr1 a')
                item_name = item_name_element.get_attribute('title')
                item_link = item_name_element.get_attribute('href')

                # Attempt to find and extract the sold count
                try:
                    sold_count = item.find_element(By.CSS_SELECTOR, '.msi5M').text
                except NoSuchElementException:
                    sold_count = "null"

                # Attempt to find and extract the ratings count
                try:
                    ratings_count= item.find_element(By.CSS_SELECTOR, '.qzqFw').text
                except NoSuchElementException:
                    ratings_count = "null"

                location = item.find_element(By.CSS_SELECTOR, '.p8k2h').text

                price = item.find_element(By.CSS_SELECTOR, '.ooOxS').text.split()[0]  # Extract the price part

                # Append the extracted information to the scraped_data list
                scraped_data.append([item_name, item_link,sold_count, ratings_count, location, price])
                
            except Exception as e:
                print(f"Error processing item: {e}")
        
    # Open a CSV file in write mode
    with open('scraped_data.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        # Create a CSV writer object
        csv_writer = csv.writer(csvfile)
        
        # Write header row
        csv_writer.writerow(['Item Name', 'Item Link','Sold Count', 'Ratings Count', 'Location', 'Price'])
        
        # Iterate through each product item and write to CSV
        for item in scraped_data:
            csv_writer.writerow(item)

    # Close the WebDriver
    driver.quit()

    return scraped_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        link = request.form['link']
        num_pages = int(request.form['num_pages'])

        # Scrape data
        scraped_data = scrape_lazada_products(link, num_pages)

        return render_template('index.html', data=scraped_data)
    else:
        return render_template('index.html', data=[])
    
@app.route('/download', methods=['POST'])
def download():
    return send_file('scraped_data.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
