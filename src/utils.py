from redfin import Redfin
import requests
import hashlib
import pandas as pd
import time
def get_info_from_address(address):
        client = Redfin()
        try:
            response = client.search(address)
        except:
            time.sleep(10)
            try:
                print("There was an issue connecting to the API; attempting reconnection")
                response =  client.search(address)
            except:
                return "The connection has timed out; please try adding a house again in some time"
        try:
            url = response['payload']['exactMatch']['url']
            initial_info = client.initial_info(url)
            property_id = initial_info['payload']['propertyId']
            listing_id = initial_info['payload']['listingId']
        except:
            try:
                url = response['payload']['sections'][0]['rows'][0]['url']
                initial_info = client.initial_info(url)
                property_id = initial_info['payload']['propertyId']
                listing_id = initial_info['payload']['listingId']
            except:
                return "There was an issue with the entered address"

        
        mls = client.below_the_fold(property_id)['payload']
        info = client.avm_details(property_id, listing_id)['payload']
        
        
        
        restimate = info['sectionPreviewText']
        beds = info['numBeds']
        baths = info['numBaths']
        
        sqft = info['sqFt']['value']
            
        
        string = url.strip("/")
        parts = string.split("/")

        state = parts[0]
        city = parts[1].replace("-", " ")
        initial = parts[2].split("-")
        zip_code = initial[-1]
        initial.pop()
        addy = " ".join(initial)

        
        try: 
            land_sq_ft = mls['amenitiesInfo']['superGroups'][1]['amenityGroups'][3]['amenityEntries'][1]['amenityValues'][0]
        except:
            land_sq_ft = None
        try:  
            parking_spaces =  mls['amenitiesInfo']['superGroups'][1]['amenityGroups'][2]['amenityEntries'][0]['amenityValues'][0]
        except:
            parking_spaces = None
        
        try:
            parking_type = mls['amenitiesInfo']['superGroups'][1]['amenityGroups'][2]['amenityEntries'][1]['amenityValues'][0]
        except:
            parking_type = None
        
        try: 
            home_type = mls['amenitiesInfo']['superGroups'][1]['amenityGroups'][0]['amenityEntries'][3]['amenityValues'][0]
        except: 
            home_type = "New"
        try:
            og_price = info['lastSoldPrice']
        except:
            og_price = "N/A"
        
        dict = {"address":addy, "city": city, "state": state, "zip_code" : zip_code, "beds" : beds, "baths" : baths, "zestimate":restimate, 
        "og_price": og_price, "sq_ft": sqft, "parking": parking_spaces, "lot_size" : land_sq_ft, "parking_type": parking_type, "home_type":home_type}
        return dict

def get_closest_loan_term(initial_value):
    value1 = 30
    value2 = 20
    value3 = 15
    # Calculate the absolute differences
    
    diff1 = abs(initial_value - value1)
    diff2 = abs(initial_value - value2)
    diff3 = abs(initial_value - value3)

    # Compare the differences and assign the closest value
    if diff1 <= diff2 and diff1 <= diff3:
        closest_value = 'thirtyYearFixed'
    elif diff2 <= diff1 and diff2 <= diff3:
        closest_value = 'twentyYearFixed'
    else:
        closest_value = 'fifteenYearFixed'

    # Output the closest value
    return closest_value