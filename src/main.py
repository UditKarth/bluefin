from scraper import *
import concurrent.futures
import time
import threading
import PySimpleGUI as sg
from queue import Queue

homes = Homes()
MAX_CHUNK_SIZE = 35
DELAY_SECONDS = 1
def process_data(city, state, max_price, address, progress_queue):
    if address is not None:
        # Address search
        homes.add_info_from_address(address)
        progress_queue.put(1)
    elif city is not None and state is not None and max_price is not None:
        # City search
        addresses = get_addresses(city, state, max_price)
        total_addresses = len(addresses)
        processed_addresses = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            chunks = [addresses[i:i + MAX_CHUNK_SIZE] for i in range(0, total_addresses, MAX_CHUNK_SIZE)]
            for chunk in chunks:
                for address in chunk:
                    executor.submit(homes.add_info_from_address, address)
                    processed_addresses += 1
                    progress_queue.put(processed_addresses / total_addresses)
                    time.sleep(DELAY_SECONDS)
                time.sleep(DELAY_SECONDS)
        progress_queue.put(1)
def main_city_search(city, state, max_price, progress_bar, window_wait):
    addresses = get_addresses(city, state, max_price)

    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        chunks = [addresses[i:i + MAX_CHUNK_SIZE] for i in range(0, len(addresses), MAX_CHUNK_SIZE)]
        for i, chunk in enumerate(chunks):
            for address in chunk:
                executor.submit(process_data, city, state, max_price, address)
                time.sleep(DELAY_SECONDS)
            progress_bar.UpdateBar(i + 1, len(chunks))
            time.sleep(DELAY_SECONDS)

def main_address_search(address, progress_bar, window_wait):
    process_data(None, None, None, address)
    progress_bar.UpdateBar(1, 1)


def search_interface():
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
                # City search
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

                        # Create a waiting window
                        layout_wait = [
                            [sg.Text("Please wait while the data is being processed...")],
                            [sg.ProgressBar(1, orientation='h', size=(20, 20), key='-PROGRESS-')]
                        ]
                        window_wait = sg.Window("Processing", layout_wait, finalize=True)
                        progress_bar = window_wait['-PROGRESS-']
                        progress_queue = Queue()

                        # Start a new thread to execute the main function
                        thread = threading.Thread(target=process_data, args=(city, state, max_price, None, progress_queue))
                        thread.daemon = True
                        thread.start()

                        while thread.is_alive():
                            event, values = window_wait.read(timeout=100)
                            if event == sg.WINDOW_CLOSED:
                                break
                            if not progress_queue.empty():
                                progress = progress_queue.get()
                                progress_bar.UpdateBar(progress, 1)

                        window_wait.close()

                    cont = sg.PopupYesNo("Would you like to search with new search terms?", title="Continue Search")
                    if cont == 'No':
                        break
                window2.close()
                break
            elif search_type == "2":
                # Address search
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

                        # Create a waiting window
                        layout_wait = [
                            [sg.Text("Please wait while the data is being processed...")],
                            [sg.ProgressBar(1, orientation='h', size=(20, 20), key='-PROGRESS-')]
                        ]
                        window_wait = sg.Window("Processing", layout_wait, finalize=True)
                        progress_bar = window_wait['-PROGRESS-']
                        progress_queue = Queue()

                        # Start a new thread to execute the main function
                        thread = threading.Thread(target=process_data, args=(None, None, None, address, progress_queue))
                        thread.daemon = True
                        thread.start()

                        while thread.is_alive():
                            event, values = window_wait.read(timeout=100)
                            if event == sg.WINDOW_CLOSED:
                                break
                            if not progress_queue.empty():
                                progress = progress_queue.get()
                                progress_bar.UpdateBar(progress, 1)

                        window_wait.close()

                    cont = sg.PopupYesNo("Would you like to search for another address?", title="Continue Search")
                    if cont == 'No':
                        break
                window3.close()
                break
            else:
                sg.popup("There was an issue with the entered value; please try again")
                continue

    window1.close()
    if homes.reet.empty and homes.house_data.empty:
        return "There were no results for the given search terms."
    else:
        return homes

def main():
    

    homes_result = search_interface()

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
            [sg.Button("Search again")],
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
            if event4 == "Search again":
                main()
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

if __name__ == "__main__":
    main()