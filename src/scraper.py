from selenium.webdriver import Chrome
import logging
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
import threading
import PySimpleGUI as sg


# Disable console messages
logging.getLogger('selenium').setLevel(logging.CRITICAL)

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

def main():
    # parser = argparse.ArgumentParser(description="Redfin Web Scraper")
    # parser.add_argument("--search_type", help="Select search type: 1 for city search, 2 for address search")
    # args = parser.parse_args()
    MAX_CHUNK_SIZE = 35
    DELAY_SECONDS = 1

    layout1 = [
        [sg.Text("Select search type: 1 for city search, 2 for address search")],
        [sg.Input(key="-SEARCH_TYPE-")],
        [sg.Button("Next")]
    ]

    window1 = sg.Window("Redfin Web Scraper - Search Type", layout1)

    while True:
        event1, values1 = window1.read()
        if event1 == sg.WINDOW_CLOSED:
            break
        elif event1 == "Next":
            layout_wait = [
                [sg.Text("Please wait while the data is being processed...")],
                [sg.ProgressBar(1, orientation='h', size=(20, 20), key='-PROGRESS-')]
            ]
            window_wait = sg.Window("Processing", layout_wait, finalize=True)
            progress_bar = window_wait['-PROGRESS-']
            progress_bar.UpdateBar(0, 1)

            # Start a new thread to execute the main function
            thread = threading.Thread(target=main)
            thread.daemon = True
            thread.start()

            while thread.is_alive():
                event, values = window_wait.read(timeout=100)
                if event == sg.WINDOW_CLOSED:
                    break

            window_wait.close()
            search_type = values1["-SEARCH_TYPE-"]
            if search_type == "1":
                layout2 = [
                    [sg.Text("Enter the name of the city: "), sg.Input(key="-CITY-")],
                    [sg.Text("Enter the state abbreviation: "), sg.Input(key="-STATE-")],
                    [sg.Text("Enter the maximum price (as a number): "), sg.Input(key="-MAX_PRICE-")],
                    [sg.Button("Search")]
                ]
                window2 = sg.Window("Redfin Web Scraper - City Search", layout2)
                while True:
                    event2, values2 = window2.read()
                    if event2 == sg.WINDOW_CLOSED:
                        break
                    elif event2 == "Search":
                        city = values2["-CITY-"]
                        state = values2["-STATE-"]
                        max_price = values2["-MAX_PRICE-"]
                        if not city:
                            sg.popup("City name cannot be empty. Please try again.")
                            continue
                        if not state:
                            sg.popup("State abbreviation cannot be empty. Please try again.")
                            continue
                        if not max_price.isdigit() or int(max_price) <= 0:
                            sg.popup("Max price must be a positive integer. Please try again.")
                            continue
                        
                        addresses = get_addresses(city, state, max_price)
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
                            chunks = [addresses[i:i+MAX_CHUNK_SIZE] for i in range(0, len(addresses), MAX_CHUNK_SIZE)]
                            for chunk in chunks:
                                for address in chunk:
                                    executor.submit(homes.add_info_from_address, address)
                                    time.sleep(DELAY_SECONDS)
                            time.sleep(DELAY_SECONDS)

                        cont = sg.PopupYesNo("Would you like to search with new search terms?", title="Continue Search")
                        if cont == 'no':
                            break
                        if cont.lower() != 'yes':
                            break
                window2.close()

            elif search_type == "2":
                layout3 = [
                    [sg.Text("Enter the address: "), sg.Input(key="-ADDRESS-")],
                    [sg.Button("Search")]
                ]
                window3 = sg.Window("Redfin Web Scraper - Address Search", layout3)
                while True:
                    event3, values3 = window3.read()
                    if event3 == sg.WINDOW_CLOSED:
                        break
                    elif event3 == "Search":
                        address = values3["-ADDRESS-"]
                        if not address:
                            sg.popup("Address cannot be empty. Please try again.")
                            continue
                        homes.add_info_from_address(address)
                        cont = sg.PopupYesNo("Would you like to search for another address?", title="Continue Search")
                        if cont.lower() != 'yes':
                            break
                window3.close()

            else:
                sg.popup("There was an issue with the entered value; please try again")
                continue

        # Prompt the user to choose the search type again
        # args.search_type = sg.popup_get_text("Select search type: 1 for city search, 2 for address search (or press Enter to exit):",
        #                                      title="Search Type")
        # if not args.search_type:
        #     break

    window1.close()
    if homes.reet.empty and homes.house_data.empty:
        return "There were no results for the given search terms."
    else:
        return homes
    

if __name__ == "__main__":
    homes_result = main()

    if isinstance(homes_result, str):
        sg.popup(homes_result)
    else:
        layout4 = [
            [sg.Text("House Data:")],
            [sg.Table(homes_result.get_data().values.tolist(),
                      headings=homes_result.get_data().columns.tolist(),
                      auto_size_columns=False,
                      col_widths=25,
                      display_row_numbers=False,
                      justification='left',
                      num_rows=10,
                      enable_events=True,
                      vertical_scroll_only=False,
                      key="-TABLE_HOUSE_DATA-")],
            [sg.Text("REET Data:")],
            [sg.Table(homes_result.get_reet().values.tolist(),
                      headings=homes_result.get_reet().columns.tolist(),
                      auto_size_columns=False,
                      col_widths=25,
                      display_row_numbers=False,
                      justification='left',
                      num_rows=10,
                      enable_events=True,
                      vertical_scroll_only=False,
                      key="-TABLE_REET_DATA-")],
            [sg.Button("Export to CSV")],
            [sg.Button("Further query")],
            [sg.Button("Exit")]
        ]
        window4 = sg.Window("Redfin Web Scraper - Data", layout4)
        while True:
            event4, values4 = window4.read()
            if event4 == sg.WINDOW_CLOSED or event4 == "Exit":
                break
            if event4 == "Export to CSV":
                homes_result.csv()
                sg.popup("Exported to CSV")
            if event4 == "Further query":
                layout5 = [
                    [sg.Text("Would you like to query by house data or by financial data?")],
                    [sg.Button("House Data")],
                    [sg.Button("Financial Data")],
                    [sg.Button("Exit")]
                ]
                window5 = sg.Window("Redfin Web Scraper - Further Query", layout5)
                while True:
                    event5, values5 = window5.read()
                    if event5 == sg.WINDOW_CLOSED or event5 == "Exit":
                        break
                    if event5 == "House Data":
                        layout6 = [
                            [sg.Text("Enter the column name: "), sg.Input(key="-COLUMN_NAME_HOUSE-")],
                            [sg.Text("Enter the value: "), sg.Input(key="-VALUE_HOUSE-")],
                            [sg.Button("Search")],
                            [sg.Button("Back")]
                        ]
                        window6 = sg.Window("Redfin Web Scraper - Further Query - House Data", layout6)
                        while True:
                            event6, values6 = window6.read()
                            if event6 == sg.WINDOW_CLOSED or event6 == "Back":
                                break
                            if event6 == "Search":
                                column_name_house = values6["-COLUMN_NAME_HOUSE-"]
                                value_house = values6["-VALUE_HOUSE-"]
                                if not column_name_house:
                                    sg.popup("Column name cannot be empty. Please try again.")
                                    continue
                                if not value_house:
                                    sg.popup("Value cannot be empty. Please try again.")
                                    continue
                                selected_house_layout = [
                                    [sg.Text("Selected House Data:")],
                                    [sg.Table(homes_result.query_house_data(column_name_house, value_house).values.tolist(),
                                              headings=homes_result.get_data().columns.tolist(),
                                              auto_size_columns=False,
                                              col_widths=25,
                                              display_row_numbers=False,
                                              justification='left',
                                              num_rows=10,
                                              enable_events=True,
                                              vertical_scroll_only=False,
                                              key="-SELECTED_TABLE_HOUSE_DATA-")],
                                    [sg.Button("Export to CSV")],
                                    [sg.Button("Back")]
                                ]
                                window7 = sg.Window("Redfin Web Scraper - Further Query - House Data - Results", selected_house_layout)
                                while True:
                                    event7, values7 = window7.read()
                                    if event7 == sg.WINDOW_CLOSED or event7 == "Back":
                                        break
                                    if event7 == "Export to CSV":
                                        homes_result.query_house_data(column_name_house, value_house).csv()
                                        sg.popup("Exported to CSV")
                                window7.close()
                        window6.close()
                    if event5 == "Financial Data":
                        layout8 = [
                            [sg.Text("Enter the column name: "), sg.Input(key="-COLUMN_NAME_FINANCIAL-")],
                            [sg.Text("Enter the value: "), sg.Input(key="-VALUE_FINANCIAL-")],
                            [sg.Button("Search")],
                            [sg.Button("Back")]
                        ]
                        window8 = sg.Window("Redfin Web Scraper - Further Query - Financial Data", layout8)
                        while True:
                            event8, values8 = window8.read()
                            if event8 == sg.WINDOW_CLOSED or event8 == "Back":
                                break
                            if event8 == "Search":
                                column_name_financial = values8["-COLUMN_NAME_FINANCIAL-"]
                                value_financial = values8["-VALUE_FINANCIAL-"]
                                if not column_name_financial:
                                    sg.popup("Column name cannot be empty. Please try again.")
                                    continue
                                if not value_financial:
                                    sg.popup("Value cannot be empty. Please try again.")
                                    continue
                                selected_financial_layout = [
                                    [sg.Text("Selected Financial Data:")],
                                    [sg.Table(homes_result.query_reet(column_name_financial, value_financial).values.tolist(),
                                              headings=homes_result.get_reet().columns.tolist(),
                                              auto_size_columns=False,
                                              col_widths=25,
                                              display_row_numbers=False,
                                              justification='left',
                                              num_rows=10,
                                              enable_events=True,
                                              vertical_scroll_only=False,
                                              key="-SELECTED_TABLE_REET_DATA-")],
                                    [sg.Button("Export to CSV")],
                                    [sg.Button("Back")]
                                ]
                                window9 = sg.Window("Redfin Web Scraper - Further Query - Financial Data - Results", selected_financial_layout)
                                while True:
                                    event9, values9 = window9.read()
                                    if event9 == sg.WINDOW_CLOSED or event9 == "Back":
                                        break
                                    if event9 == "Export to CSV":
                                        homes_result.query_reet(column_name_financial, value_financial).csv()
                                        sg.popup("Exported to CSV")
                                window9.close()
                        window8.close()
                window5.close()
        window4.close()