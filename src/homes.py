from house import *
import re
import numpy_financial as npf
 

class Homes:
    def __init__(self):
        #House data is used to contain the physical information of the hosue; ie # of beds, baths, an estimate of the price etc. 
        self.house_data = pd.DataFrame()

        #REET is designed to contain the financial information of the house
        self.reet = pd.DataFrame()

        #Client is used to query Redfin
        self.client = Redfin()
    
    #Prints out only the house data 
    def __repr__(self):
        return self.house_data.to_string()
    
    #Adds a House class object to Homes house_data
    #DEPRECATED: REPLACED WITH add_address
    # def add_house(self, house):
    #     if ( house.street_address is not None and house != "There is no data for this house"):
    #         self.house_data = pd.concat([self.house_data, pd.DataFrame([house.as_dict()])], ignore_index=True)
    
    #Queries the given address, makes it a House object then inserts the house into Homes house_data
    def add_address(self, address):
        house = get_info_from_address(address)
        if house != "There was an issue with the entered address":
            self.house_data = pd.concat([self.house_data, pd.DataFrame([house])], ignore_index=True)
        
    
    #Removes house based on name from house_data only 
    #NOTE: The function can remove houses when given a shorter string than the address 
    #(ie. given that user wants to remove '4544 Radnor Street', the user could input "4544 Radnor"
    # and the house would be removed). As a result, be careful when inputting shortened information like "4544",
    #as this will remove instances where the address contains "4544"
    def remove_house_data(self, house_name):
        pre_len = len(self.house_data)
        if pre_len == 0:
            return "The dataframe is empty"
        matching_indices = self.house_data['address'].str.contains(house_name, case=False) 
        self.house_data = self.house_data[~matching_indices].reset_index(drop=True)
        #self.house_data = self.house_data[self.house_data['address'] != house_name].reset_index(drop=True)
        post_len = len(self.house_data)
        if pre_len == post_len:
            return "There may have been a typo with the entered address"
    

    #Removes address from both reet and house_data
    #NOTE: The function can remove houses when given a shorter string than the address 
    #(ie. given that user wants to remove '4544 Radnor Street', the user could input "4544 Radnor"
    # and the house would be removed). As a result, be careful when inputting shortened information like "4544",
    #as this will remove instances where the address contains "4544"
    def remove_house(self, address):
        house_lenp = len(self.house_data)
        reet_lenp = len(self.reet)
        if reet_lenp == 0 and house_lenp == 0:
            return "Both dataframes are empty"
        elif reet_lenp == 0:
            return "The REET dataframe is empty; use remove_house_data if you would like to remove remaining houses"
        elif house_lenp == 0:
            return "The house dataframe is empty"

        hmatching_indices = self.house_data['address'].str.contains(address, case=False)
        self.house_data = self.house_data[~hmatching_indices].reset_index(drop=True)
        

        rmatching_indices = self.reet['address'].str.contains(address, case=False)
        self.reet = self.reet[~rmatching_indices].reset_index(drop=True)

        post_len = len(self.reet)
        if reet_lenp == post_len:
            return "There may have been a typo with the entered address"

    #Clears the dataframe and creates a new, empty dataframe
    def empty_data(self):
        self.reet = pd.DataFrame()
        self.house_data = pd.DataFrame()

        
    #Returns the dataframe for the house_data
    def get_data(self):
        return self.house_data
    
    #Returns reet dataframe
    def get_reet(self):
        return self.reet
    
    #Goes through house_data and removes the data which had a faulty URL and returned as None;
    #Doesn't remove new houses which have None for certain columns
    def clean_house_data(self):
        self.house_data.dropna()
        mask = self.house_data.isna().all(axis=1)
        new_mask = self.house_data['home_type'].str.contains('New', case=False, na=False)
        remove_mask = mask & ~new_mask
        self.data = self.house_data[~remove_mask].reset_index(drop=True)
    
    #Main function: given an address, the function will concat the house information from redfin to  
    #the house_data, calculate the financial viability of the house, store it as a dictionary and append
    #the dictionary to the reet dataframe
    def add_info_from_address(self, address):
        client = self.client
        house = House()
        try:
            response = client.search(address)
        except:
            print("There was an issue connecting to the API; attempting reconnection")
            time.sleep(10)
            try:
                response =  client.search(address)
            except:
                return "The connection has timed out; please try again in some time"
        try:
            url = response['payload']['exactMatch']['url']
            initial_info = client.initial_info(url); property_id = initial_info['payload']['propertyId']; listing_id = initial_info['payload']['listingId']
            mls = client.below_the_fold(property_id)['payload']
            info = client.avm_details(property_id, listing_id)['payload']
            coh = client.cost_of_home_ownership(property_id)['payload']['mortgageCalculatorInfo']
            rent = client.rental_estimate(property_id, listing_id)['payload']            
        except:
                try:
                    url = response['payload']['sections'][0]['rows'][0]['url']
                    initial_info = client.initial_info(url); property_id = initial_info['payload']['propertyId']; listing_id = initial_info['payload']['listingId']
                    mls = client.below_the_fold(property_id)['payload']
                    info = client.avm_details(property_id, listing_id)['payload']
                    coh = client.cost_of_home_ownership(property_id)['payload']['mortgageCalculatorInfo']
                    rent = client.rental_estimate(property_id, listing_id)['payload']            
                except:
                    return "There was an issue with the given address; please try again"

        try:
            restimate = info['sectionPreviewText']
        except:
            restimate = None 
        try:
            beds = info['numBeds']
        except:
            beds = None
        try:
            baths = info['numBaths']
        except:
            baths = None
        try:

            sqft = info['sqFt']['value']
        except:
            sqft = None
        
        string = url.strip("/"); parts = string.split("/")
        state = parts[0]; city = parts[1].replace("-", " "); initial = parts[2].split("-"); zip_code = initial[-1]; initial.pop(); addy = " ".join(initial)
        
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
        house = House()
        house.street_address = addy; house.city = city; house.state = state; house.zip_code = zip_code; house.beds = beds; house.baths = baths
        house.zestimate = restimate; house.og_price = og_price; house.sq_ft = sqft; house.parking = parking_spaces; house.lot_size = land_sq_ft; house.parking_type = parking_type; house.home_type = home_type
        
        self.house_data = pd.concat([self.house_data, pd.DataFrame([house.as_dict()])], ignore_index=True)
        
        #REET PART
        ##########################################
        #Assuming these values, change if needed##
        ##########################################
        cc = 6000
        lt = 30

        try:
            price = float(info['predictedValue'])
        except:
            try:
                price = float(info['priceInfo']['amount'])
            except:
                return "There was an issue retrieving the price"
        down = float(coh['downPaymentPercentage'])
        dp = price * down/100
        
        loan_cost = price - dp + cc
        # if (lt.isnumeric() == False):
        #     print("Inputted invalid number; setting loan_term = 30")
        #     lt = 30
        if lt == 30:
            length_of_loan = 'thirtyYearFixed'
        elif lt == 20:
            length_of_loan = 'twentyYearFixed'
        elif lt == 15:
            length_of_loan = 'fifteenYearFixed'
        else:
            length_of_loan = get_closest_loan_term(lt)

        ir = float(coh['mortgageRateInfo'][length_of_loan])
        mm = npf.pmt(ir/100/12, lt*12, -1 * loan_cost, 0)
        
        try: 
            hoa = re.findall(r'\d+', client.info_panel(property_id, listing_id)['payload']['mainHouseInfo']['selectedAmenities'][0]['content'])
            hoa = float(hoa[0])
        except:
            hoa = 0
            
        pt = float(coh['propertyTaxRate'])
        mpt = (price*(pt/100))/12
        mhi = float(coh['homeInsuranceRate'])/12/100 * price

        me = (mhi + mm + hoa + mpt)
        
        try:
            mr = float(rent['rentalEstimateInfo']['predictedValue'])
            cf = mr - me
        except:
            mr = 0
            cf = 0
        ar = mr * 12
        acf = cf * 12
        cr = ((ar - 12*(me-mm))/(price + cc))*100
        ccr = (acf/(dp + cc))*100
        reet = {
            'address': addy,
            'purchase_estimate': price,
            'down%': down,
            'down_payment': dp,
            'closing_costs': cc,
            'loan_amount': loan_cost,
            'loan_term': lt,
            'interest_rate': ir,
            'monthly_mortgage': mm,
            'monthly_hoa': hoa,
            'property_tax_rate': pt,
            'monthly_property_tax': mpt,
            'monthly_home_insurance': mhi,
            'monthly_rent': mr,
            'annural_rent': ar,
            'monthly_expenses': me,
            'monthly_cash_flow': cf,
            'annual_cash_flow': acf,
            'cap_rate': cr,
            'cash_on_cash_return': ccr
        }
        self.reet = pd.concat([self.reet, pd.DataFrame([reet])], ignore_index=True)
    

    #Sends information from the given address to the user as a dictionary
    def info_to_dict(self, address):
        client = self.client
        try:
            response = client.search(address)
        except:
            print("There was an issue connecting to the API; attempting reconnection")
            time.sleep(10)
            try:
                response =  client.search(address)
            except:
                return "The connection has timed out; please try again in some time"
        try:
            url = response['payload']['exactMatch']['url']
            initial_info = client.initial_info(url); property_id = initial_info['payload']['propertyId']; listing_id = initial_info['payload']['listingId']
            mls = client.below_the_fold(property_id)['payload']
            info = client.avm_details(property_id, listing_id)['payload']
            coh = client.cost_of_home_ownership(property_id)['payload']['mortgageCalculatorInfo']
            rent = client.rental_estimate(property_id, listing_id)['payload']            
        except:
                try:
                    url = response['payload']['sections'][0]['rows'][0]['url']
                    initial_info = client.initial_info(url); property_id = initial_info['payload']['propertyId']; listing_id = initial_info['payload']['listingId']
                    mls = client.below_the_fold(property_id)['payload']
                    info = client.avm_details(property_id, listing_id)['payload']
                    coh = client.cost_of_home_ownership(property_id)['payload']['mortgageCalculatorInfo']
                    rent = client.rental_estimate(property_id, listing_id)['payload']            
                except:
                    return "There was an issue with the given address; please try again"

        try:
            restimate = info['sectionPreviewText']
        except:
            restimate = None 
        try:
            beds = info['numBeds']
        except:
            beds = None
        try:
            baths = info['numBaths']
        except:
            baths = None
        try:

            sqft = info['sqFt']['value']
        except:
            sqft = None
        
        string = url.strip("/"); parts = string.split("/")
        state = parts[0]; city = parts[1].replace("-", " "); initial = parts[2].split("-"); zip_code = initial[-1]; initial.pop(); addy = " ".join(initial)
        
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
        house_info = {
            'address': addy,
            'city': city,
            'state': state,
            'zip_code': zip_code,
            'beds': beds,
            'baths': baths,
            'sqft': sqft,
            'land_sq_ft': land_sq_ft,
            'parking_spaces': parking_spaces,
            'parking_type': parking_type,
            'home_type': home_type,
            'original_price': og_price,
            'restimate': restimate
        }
        
        #REET PART
        ##########################################
        #Assuming these values, change if needed##
        ##########################################
        cc = 6000
        lt = 30

        try:
            price = float(info['predictedValue'])
        except:
            try:
                price = float(info['priceInfo']['amount'])
            except:
                return "There was an issue retrieving the price"
        down = float(coh['downPaymentPercentage'])
        dp = price * down/100
        
        loan_cost = price - dp + cc
        # if (lt.isnumeric() == False):
        #     print("Inputted invalid number; setting loan_term = 30")
        #     lt = 30
        if lt == 30:
            length_of_loan = 'thirtyYearFixed'
        elif lt == 20:
            length_of_loan = 'twentyYearFixed'
        elif lt == 15:
            length_of_loan = 'fifteenYearFixed'
        else:
            length_of_loan = get_closest_loan_term(lt)

        ir = float(coh['mortgageRateInfo'][length_of_loan])
        mm = npf.pmt(ir/100/12, lt*12, -1 * loan_cost, 0)
        
        try: 
            hoa = re.findall(r'\d+', client.info_panel(property_id, listing_id)['payload']['mainHouseInfo']['selectedAmenities'][0]['content'])
            hoa = float(hoa[0])
        except:
            hoa = 0
            
        pt = float(coh['propertyTaxRate'])
        mpt = (price*(pt/100))/12
        mhi = float(coh['homeInsuranceRate'])/12/100 * price

        me = (mhi + mm + hoa + mpt)
        
        try:
            mr = float(rent['rentalEstimateInfo']['predictedValue'])
            cf = mr - me
        except:
            mr = 0
            cf = 0
        ar = mr * 12
        acf = cf * 12
        cr = ((ar - 12*(me-mm))/(price + cc))*100
        ccr = (acf/(dp + cc))*100
        reet = {
            'address': addy,
            'purchase_estimate': price,
            'down%': down,
            'down_payment': dp,
            'closing_costs': cc,
            'loan_amount': loan_cost,
            'loan_term': lt,
            'interest_rate': ir,
            'monthly_mortgage': mm,
            'monthly_hoa': hoa,
            'property_tax_rate': pt,
            'monthly_property_tax': mpt,
            'monthly_home_insurance': mhi,
            'monthly_rent': mr,
            'annural_rent': ar,
            'monthly_expenses': me,
            'monthly_cash_flow': cf,
            'annual_cash_flow': acf,
            'cap_rate': cr,
            'cash_on_cash_return': ccr
        }
        return {'house_info':house_info, 'reet:':reet}

    # #Given a column name (str) and a condition (str), this function queries the REET dataframe and 
    # # returns only the houses which fit the condition
    # def query_reet(self, data, condition):
    #     df = self.get_reet()
    #     fin_df = pd.DataFrame()
    #     try:
    #         if condition.startswith('='):
    #             condition_value = float(condition[1:])
    #             fin_df = df[df[data] == condition_value]
    #         elif condition.startswith('<='):
    #             condition_value = float(condition[2:])
    #             fin_df = df[df[data] <= condition_value]
    #         elif condition.startswith('<'):
    #             condition_value = float(condition[1:])
    #             fin_df = df[df[data] < condition_value]
    #         elif condition.startswith('>='):
    #             condition_value = float(condition[2:])
    #             fin_df = df[df[data] >= condition_value]
    #         elif condition.startswith('>'):
    #             condition_value = float(condition[1:])
    #             fin_df = df[df[data] > condition_value]
    #         else:
    #             fin_df = df[df[data] == condition]
                
    #     except:
    #         return "There was an issue with some of the data you entered"
            
    #     if fin_df.empty:
    #         return "There were no results =("
    #     else:
    #         return fin_df 

    # #Given a column name (str) and a condition (str), this function queries the house_data dataframe 
    # #and returns only the houses which fit the condition
    # def query_house_data(self, data, condition):
    #     df = self.get_data()
    #     fin_df = pd.DataFrame()
    #     try:
    #         if condition.startswith('='):
    #             condition_value = float(condition[1:])
    #             fin_df = df[df[data] == condition_value]
    #         elif condition.startswith('<='):
    #             condition_value = float(condition[2:])
    #             fin_df = df[df[data] <= condition_value]
    #         elif condition.startswith('<'):
    #             condition_value = float(condition[1:])
    #             fin_df = df[df[data] < condition_value]
    #         elif condition.startswith('>='):
    #             condition_value = float(condition[2:])
    #             fin_df = df[df[data] >= condition_value]
    #         elif condition.startswith('>'):
    #             condition_value = float(condition[1:])
    #             fin_df = df[df[data] > condition_value]
    #         else:
    #             fin_df = df[df[data] == condition]
                    
    #     except:
    #         print("There was an issue with some of the data you entered")

    #     if fin_df.empty:
    #         print("There were no results =(")
    #     else:
    #         return fin_df 

    def query_reet(self, data, condition):
        reet_df = self.get_reet()
        house_df = self.get_data()

        fin_df = pd.DataFrame()
        try:
            if data in reet_df.columns:  # Check if the column exists in reet_df
                if condition.startswith('='):
                    condition_value = float(condition[1:])
                    fin_df = reet_df[reet_df[data] == condition_value]
                elif condition.startswith('<='):
                    condition_value = float(condition[2:])
                    fin_df = reet_df[reet_df[data] <= condition_value]
                elif condition.startswith('<'):
                    condition_value = float(condition[1:])
                    fin_df = reet_df[reet_df[data] < condition_value]
                elif condition.startswith('>='):
                    condition_value = float(condition[2:])
                    fin_df = reet_df[reet_df[data] >= condition_value]
                elif condition.startswith('>'):
                    condition_value = float(condition[1:])
                    fin_df = reet_df[reet_df[data] > condition_value]
                else:
                    fin_df = reet_df[reet_df[data] == condition]
            else:
                print("The column", data, "does not exist in reet_df")
                return
            
        except:
            print("There was an issue with some of the data you entered")
            return
        
        if fin_df.empty:
            print("There were no results =(")
        else:
            merged_df = pd.merge(fin_df, house_df, on="address", how="inner")
            return merged_df

    def query_house_data(self, data, condition):
        house_df = self.get_data()
        reet_df = self.get_reet()

        fin_df = pd.DataFrame()
        try:
            if condition.startswith('='):
                condition_value = float(condition[1:])
                fin_df = house_df[house_df[data] == condition_value]
            elif condition.startswith('<='):
                condition_value = float(condition[2:])
                fin_df = house_df[house_df[data] <= condition_value]
            elif condition.startswith('<'):
                condition_value = float(condition[1:])
                fin_df = house_df[house_df[data] < condition_value]
            elif condition.startswith('>='):
                condition_value = float(condition[2:])
                fin_df = house_df[house_df[data] >= condition_value]
            elif condition.startswith('>'):
                condition_value = float(condition[1:])
                fin_df = house_df[house_df[data] > condition_value]
            else:
                fin_df = house_df[house_df[data] == condition]
                    
        except:
            print("There was an issue with some of the data you entered")

        if fin_df.empty:
            print("There were no results =(")
        else:
            merged_df = pd.merge(fin_df, reet_df, on="address", how="inner")
            return merged_df

    # Remove duplicates from both DataFrames
    def remove_duplicates(self):
        self.house_data = self.house_data.drop_duplicates()
        self.reet = self.reet.drop_duplicates()

    #Converts house_data and reet to CSV files and returns them both to the user
    # for conversion to excel if needed
    def csv(self):
        csv_house_data = self.house_data.to_csv(index=False)
        csv_reet = self.house_data.to_csv(index=False)
        return csv_house_data, csv_reet
    
    #Converts from CSV file to house_data and reet. Also performs checks to ensure that the data given matches 
    #the information needed for house_data and reet
    def from_csv(self, csv_house_data, csv_reet):
        df1 = pd.read_csv(pd.compat.StringIO(csv_house_data))
        df2 = pd.read_csv(pd.compat.StringIO(csv_reet))
        
        house_data_columns = ['address', 'city', 'state', 'zip_code', 'beds', 'baths', 'zestimate',
                              'og_price', 'sq_ft', 'parking', 'lot_size', 'parking_type', 'home_type']
        
        missing_columns_house_data = set(house_data_columns) - set(df1.columns)
        
        if len(missing_columns_house_data) != 0:
            raise ValueError(f"Required columns missing in house_data DataFrame: {missing_columns_house_data}")

        reet_columns = ['address', 'purchase_price', 'down%', 'down_payment', 'closing_costs',
                        'loan_amount', 'loan_term', 'interest_rate', 'monthly_mortgage', 'monthly_hoa',
                        'property_tax_rate', 'monthly_property_tax', 'monthly_home_insurance', 'monthly_rent',
                        'annual_rent', 'monthly_expenses', 'monthly_cash_flow', 'annual_cash_flow',
                        'cap_rate', 'cash_on_cash_return']
        
        missing_columns_reet = set(reet_columns) - set(df2.columns)
        
        if len(missing_columns_reet) != 0:
            raise ValueError(f"Required columns missing in reet DataFrame: {missing_columns_reet}")
        
        self.house_data = df1
        self.reet = df2
    

    # #code to visualize REET results using HTML
    # def html_reet(self):
    #     html = self.reet.to_html()
    #     return html
    
    # #code to visualize house_data results using HTML
    # def html_house_data(self):
    #     html = self.house_data.to_html()
    #     return html
    
    
