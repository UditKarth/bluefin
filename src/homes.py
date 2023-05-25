from .house import *
import re
import numpy_financial as npf
 

class Homes:
    def __init__(self):
        self.house_data = pd.DataFrame()
        self.reet = pd.DataFrame()
    
    #Prints out only the house data
    def __repr__(self):
        return self.house_data.to_string()
    
    #Adds a House class object to Homes house_data
    #DEPRECATED: REPLACED WIHT add_address
    # def add_house(self, house):
    #     if ( house.street_address is not None and house != "There is no data for this house"):
    #         self.house_data = pd.concat([self.house_data, pd.DataFrame([house.as_dict()])], ignore_index=True)
    
    #Queries address, makes it a House object then inserts the house into Homes house_data
    def add_address(self, address):
        house = get_info_from_address(address)
        if house != "There was an issue with the entered address":
            self.house_data = pd.concat([self.house_data, pd.DataFrame([house])], ignore_index=True)
        
    
    #Removes house based on name from house_data only 
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
    

    #Removes address from both
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
    
    def empty_data(self):
        self.reet = pd.DataFrame()
        self.house_data = pd.DataFrame()

        
    #Returns the dataframe of the data
    def get_data(self):
        return self.house_data
    
    #Returns reet dataframe
    def get_reet(self):
        return self.reet
    
    #Goes through data and removes the data which had a faulty URL and returned as None;
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
        client = Redfin()
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


        restimate = info['sectionPreviewText']; beds = info['numBeds']; baths = info['numBaths']; sqft = info['sqFt']['value']
        
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
        if (lt.isnumeric() == False):
            print("Inputted invalid number; setting loan_term = 30")
            lt = 30
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
            'purchase_price': price,
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
    
    #Given a column name (str) and a condition (str), this function queries the REET dataframe and 
    # returns only the houses which fit the condition
    def query_r(self, data, condition):
        df = self.get_reet()
        fin_df = pd.DataFrame()
        try:
            if condition.startswith('='):
                condition_value = float(condition[1:])
                fin_df = df[df[data] == condition_value]
            elif condition.startswith('<='):
                condition_value = float(condition[2:])
                fin_df = df[df[data] <= condition_value]
            elif condition.startswith('<'):
                condition_value = float(condition[1:])
                fin_df = df[df[data] < condition_value]
            elif condition.startswith('>='):
                condition_value = float(condition[2:])
                fin_df = df[df[data] >= condition_value]
            elif condition.startswith('>'):
                condition_value = float(condition[1:])
                fin_df = df[df[data] > condition_value]
            else:
                fin_df = df[df[data] == condition]
                
        except:
            return "There was an issue with some of the data you entered"
            
        if fin_df.empty:
            return "There were no results =("
        else:
            return fin_df 

    #Given a column name (str) and a condition (str), this function queries the house_data dataframe 
    #and returns only the houses which fit the condition
    def query_h(self, data, condition):
        df = self.get_data()
        fin_df = pd.DataFrame()
        try:
            if condition.startswith('='):
                condition_value = float(condition[1:])
                fin_df = df[df[data] == condition_value]
            elif condition.startswith('<='):
                condition_value = float(condition[2:])
                fin_df = df[df[data] <= condition_value]
            elif condition.startswith('<'):
                condition_value = float(condition[1:])
                fin_df = df[df[data] < condition_value]
            elif condition.startswith('>='):
                condition_value = float(condition[2:])
                fin_df = df[df[data] >= condition_value]
            elif condition.startswith('>'):
                condition_value = float(condition[1:])
                fin_df = df[df[data] > condition_value]
            else:
                fin_df = df[df[data] == condition]
                    
        except:
            print("There was an issue with some of the data you entered")

        if fin_df.empty:
            print("There were no results =(")
        else:
            return fin_df 
    
    # Remove duplicates from both DataFrames
    def remove_duplicates(self):
        self.house_data = self.house_data.drop_duplicates()
        self.reet = self.reet.drop_duplicates()