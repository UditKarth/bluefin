import logging
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from homes import *
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import threading


# Disable console messages
logging.getLogger('selenium').setLevel(logging.CRITICAL)

# driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))





def get_urls(city, state, max_price):
    # Set up Selenium Chrome driver
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)

    # Navigate to Redfin search page
    if (city == None or state == None or max_price == None):
        return "Please enter a city, state, and max price"
    search_url = f"https://www.redfin.com/{state}/{city}/filter/max-price={max_price}"
    driver.get(search_url)

    # Wait for the page to load and retrieve all house URLs
    driver.implicitly_wait(3)  # Increase the wait time if needed
    house_elements = driver.find_elements(By.CSS_SELECTOR, ".homecard a")
    house_urls = [element.get_attribute("href") for element in house_elements]

    # Close the browser
    driver.quit()

    return house_urls

#Extracts a given address from a URL and returns it. 
# Currently only works for houses, Redfin has different URLs for condos/apartments
def extract_address(url):
    parts = url.split("/")
    address_index = parts.index("home") - 1
    address = parts[address_index].replace("-", " ")

    initial = parts[2].split("-")
    zip_code = initial[-1]
    initial.pop()
    address = " ".join(initial)
    return address



def get_addresses(city, state, max_price):
    # Set up Selenium Chrome driver
    client = Redfin()
    city = city.upper()
    city_id = client.search(city)['payload']['sections'][0]['rows'][0]['id'].split("_")[1]
    options = Options()
    options.add_argument("--log-level=3")  # Disable console messages
    options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)

    try:
        # Navigate to Redfin search page
        if city is None or state is None or max_price is None:
            raise ValueError("Please enter a city, state, and max price")
        city = city.replace(" ", "-")
        search_url = f"https://www.redfin.com/city/{city_id}/{state}/{city}/filter/max-price={max_price}"
        # print(search_url)
        driver.get(search_url)

        not_at_end = True
        addresses = []
        # Wait for the page to load and retrieve all house HTML elements
        while not_at_end:
            driver.implicitly_wait(5)  # Increase the wait time if needed
            house_elements = driver.find_elements(By.CSS_SELECTOR, ".MapHomeCardReact.HomeCard")
            # print(house_elements)
            # Extract addresses from each house HTML element
            for element in house_elements:
                html = element.get_attribute("innerHTML")
                soup = BeautifulSoup(html, 'html.parser')
                address_span = soup.find('div', {'class': 'link-and-anchor'})
                if address_span is not None:
                    address = address_span.text.strip()
                    addresses.append(address)

            html = driver.page_source

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Find the current page element
            current_page = soup.find('a', {'class': 'selected'})

            # Get the URL of the next page
            try:
                next_page = current_page.find_next_sibling('a')
            except:
                return "There was an issue with the URL; please try again"

            if next_page is None:
                print("Last page reached")
                not_at_end = False
                break

            # Get the URL of the next page
            next_page_url = next_page['href']
            next_page_url = f"https://www.redfin.com{next_page_url}"
            next_page_url = next_page_url.replace("/page-", f"/filter/max-price={max_price}/page-")

            # Navigate to the next page
            # print(next_page_url)
            driver.get(next_page_url)
            print("Navigating to Next Page")

        # Close the browser
        driver.quit()

        return addresses

    except Exception as e:
        # Close the browser and raise an error message
        driver.quit()
        raise RuntimeError(f"An error occurred: {str(e)}")


homes = Homes()
lock = threading.Lock()
def process_address(address):
    # Call info_to_dict() and extract house_info and reet dictionaries
    result = homes.info_to_dict(address)
    house_info = result['house_info']
    reet = result['reet']
    print(house_info)
    print(reet)
    # Acquire the lock before modifying the dataframes
    lock.acquire()
    try:
        # Concatenate house_info into homes.house_data
        homes.house_data = pd.concat([homes.house_data, pd.DataFrame([house_info])], ignore_index=True)

        # Concatenate reet into homes.reet
        homes.reet = pd.concat([homes.reet, pd.DataFrame([reet])], ignore_index=True)
    finally:
        # Release the lock
        lock.release()