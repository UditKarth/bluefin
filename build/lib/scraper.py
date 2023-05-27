#IN PROGRESS

from selenium.webdriver import Chrome
import argparse
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from homes import *
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import concurrent.futures
import time


driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))





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
    city_id = client.search(city)['payload']['sections'][0]['rows'][0]['id'].split("_")[1]
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
    driver = webdriver.Chrome(options=options)

    # Navigate to Redfin search page
    if city is None or state is None or max_price is None:
        return "Please enter a city, state, and max price"
    city = city.replace(" ", "-")
    search_url = f"https://www.redfin.com/city/{city_id}/{state}/{city}/filter/max-price={max_price}"
    print(search_url)
    driver.get(search_url)

    # Wait for the page to load and retrieve all house HTML elements
    driver.implicitly_wait(5)  # Increase the wait time if needed
    house_elements = driver.find_elements(By.CSS_SELECTOR, ".MapHomeCardReact.HomeCard")
    print(house_elements)
    # Extract addresses from each house HTML element
    addresses = []
    for element in house_elements:
        html = element.get_attribute("innerHTML")
        soup = BeautifulSoup(html, 'html.parser')
        address_span = soup.find('div', {'class': 'link-and-anchor'})
        if address_span is not None:
            address = address_span.text.strip()
            addresses.append(address)
        else:
            continue  # Add a placeholder value if no address is found

    # Close the browser
    driver.quit()

    return addresses

def get_addresses(city, state, max_price):
    # Set up Selenium Chrome driver
    client = Redfin()
    city = city.upper()
    city_id = client.search(city)['payload']['sections'][0]['rows'][0]['id'].split("_")[1]
    options = Options()
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



def main():
    parser = argparse.ArgumentParser(description="Redfin Web Scraper")
    parser.add_argument("--search_type", help="Select search type: 1 for city search, 2 for address search")
    args = parser.parse_args()
    homes = Homes()
    MAX_CHUNK_SIZE = 35
    DELAY_SECONDS = 5
    while True:
        if args.search_type == "1":
            print("Search by cities")
            city = input("Enter the name of the city: ")
            state = input("Enter the state abbreviation: ")
            max_price = input("Enter the maximum price (as a number): ")
            if not city:
                print("City name cannot be empty. Please try again.")
                continue  # This will skip the remaining code and prompt for input again
            if not state:
                print("State abbreviation cannot be empty. Please try again.")
                continue  # This will skip the remaining code and prompt for input again
            if not max_price.isdigit() or int(max_price) <= 0:
                print("Max price must be a positive integer. Please try again.")
                continue
            
            addresses = get_addresses(city, state, max_price)
            # print(len(addresses))
            # for address in addresses:
            #     homes.add_info_from_address(address)
            with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            # Split addresses into chunks of maximum size MAX_CHUNK_SIZE
                chunks = [addresses[i:i+MAX_CHUNK_SIZE] for i in range(0, len(addresses), MAX_CHUNK_SIZE)]

                for chunk in chunks:
                    for address in chunk:
                        executor.submit(homes.add_info_from_address, address)

                    time.sleep(DELAY_SECONDS)
            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     # Split addresses into chunks of maximum size MAX_CHUNK_SIZE
            #     chunks = [addresses[i:i+MAX_CHUNK_SIZE] for i in range(0, len(addresses), MAX_CHUNK_SIZE)]

            #     for chunk in chunks:
            #         for address in chunk:
            #             executor.submit(homes.info_to_dict(), address)

            #         time.sleep(DELAY_SECONDS)
            # with concurrent.futures.ThreadPoolExecutor() as executor:
            #     results = []
            #     for address in addresses:
            #         print(address)
            #         result = executor.submit(homes.info_to_dict, address)
            #         print(result)
            #         results.append(result)

            #     house_dicts = []
            #     reet_dicts = []
            #     for result in concurrent.futures.as_completed(results):
            #         data = result.result()
            #         if data is not None:
            #             house_dict, reet_dict = data
            #             house_dicts.append(house_dict)
            #             reet_dicts.append(reet_dict)

            # # Merge house_data and reet dictionaries into dataframes if needed
            # if house_dicts:
            #     house_data = pd.DataFrame(house_dicts)
            #     reet_data = pd.DataFrame(reet_dicts)
            #     homes.house_data = pd.concat([homes.house_data, house_data], ignore_index=True)
            #     homes.reet = pd.concat([homes.reet, reet_data], ignore_index=True)

            cont = input("Would you like to search with new search terms? [Y/N]:]")
            if (cont.lower() != 'y'):
                break

        elif args.search_type == "2":
            print("Search by address")
            address = input("Enter the address: ")
            if not address:
                print("Address cannot be empty. Please try again.")
                continue
            homes.add_info_from_address(address)
            cont = input("Would you like to search for another address? [Y/N]:]")
            if (cont.lower() != 'y'):
                break

        else:
            print("There was an issue with the entered value; please try again")

        # Prompt the user to choose the search type again
        args.search_type = input("Select search type: 1 for city search, 2 for address search (or press Enter to exit): ")
        if not args.search_type:
            break
    if homes.reet.empty and homes.house_data.empty:
        return ("There were no results for the given search terms.")
    else:
        return homes
if __name__ == "__main__":
    homes_result = main()
    if isinstance(homes_result, str):
        print(homes_result)
    else:
        print("Homes DataFrame 1:")
        print(homes_result.house_data)
        print("Homes DataFrame 2:")
        print(homes_result.reet)