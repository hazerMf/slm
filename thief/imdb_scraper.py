from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import os

def write_quotes_to_file(quotes_list, movie_title):

    # Clean the title
    safe_title = re.sub(r'[\\/:*?"<>|]', '', movie_title).replace(' ', '_')
    filename = os.path.join("..", "food", f"{safe_title}_quotes.txt")
    
    separator = "\n" + "="*50 + "\n"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for i, quote in enumerate(quotes_list):
                if i > 0:
                    f.write(separator)
                f.write(quote + '\n')
                
        return os.path.abspath(filename)
        
    except IOError as e:
        return f"Error writing to file: {e}"


def scrape_dynamic_imdb_quotes(url):

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    
    print("--- Starting Headless Browser... ---")
    
    try:
        driver = webdriver.Chrome(service=service, options=chrome_options) 
        
        driver.get(url)
        time.sleep(10) 
        
        # Wait for title to be present
        WebDriverWait(driver, 20).until(lambda d: d.find_element(By.TAG_NAME, 'title').get_attribute('textContent').strip() != '')
        
        rendered_html = driver.page_source
        
        driver.quit()
        
        soup = BeautifulSoup(rendered_html, 'html.parser')
        
        title_tag = soup.find('title')
        movie_title = title_tag.get_text(strip=True).split(' Quotes')[0].strip() if title_tag else "Movie Quotes"

        quotes_list = []
        
        # Find all quote containers
        quote_divs = soup.find_all('div', class_='ipc-html-content') 

        if not quote_divs:
            return ["Error: No quotes found. The site structure may have changed."], movie_title

        for div in quote_divs:
            quote_text = div.get_text(strip=True)
            if len(quote_text) > 10:  # Filter short texts
                quotes_list.append(quote_text)

        return quotes_list, movie_title

    except Exception as e:
        if 'driver' in locals():
            driver.quit() # Ensure the driver closes on error
        return [f"A major error occurred during Selenium execution: {e}"], None

target_url = "https://www.imdb.com/title/tt3402138/quotes/"

quotes, title = scrape_dynamic_imdb_quotes(target_url)

if quotes and not quotes[0].startswith("Error"):
    file_path = write_quotes_to_file(quotes, title)
    print(f"Quotes saved to: {file_path}")
else:
    print("No quotes scraped or error occurred.")
    if quotes:
        print(quotes[0])
    