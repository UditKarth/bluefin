from src.homes import *
class Test_Homes:
    def setup_class(self):
        """Called before every class intialization"""
        self.homes = Homes()
        
    
    def teardown_class(self):
        del self.homes
        

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test__init__(self):
        
        assert (self.homes.house_data.empty)
        assert self.homes.reet.empty
    
    
    def test_add_address(self):
        self.homes = Homes()
        self.homes.add_address("4544 Radnor Street")
        assert len(self.homes.house_data) == 1
        self.homes.add_address("123 Nonsense Street")
        assert len (self.homes.house_data) == 1
        self.homes.add_address("")
        assert len(self.homes.house_data) == 1
        self.homes.add_address("834 N Museo Drive")
        assert len(self.homes.house_data) == 2
        assert len(self.homes.reet) == 0
        
    def test_empty_data(self):
        self.homes.empty_data()
        assert len(self.homes.house_data) == 0
        assert len(self.homes.reet) == 0
    
    
    def test_add_info_from_address(self):
        self

    def test_remove_house(self):
        self.homes = Homes()
        self.homes.add_info_from_address("4544 Radnor St")
        self.homes.add_info_from_address("834 N Museo Drive")
        print(self.homes.remove_house("4544 Radnor St"))
        assert len(self.homes.house_data) == 1
        assert len(self.homes.reet) == 1
        assert self.homes.remove_house("Non-existent house #1") == "There may have been a typo with the entered address"
        self.homes.remove_house("834 N Museo")
        assert len(self.homes.house_data) == 0
        assert len(self.homes.reet) == 0
        assert self.homes.remove_house("Non-existent house #2") == "Both dataframes are empty"
        
    
    def test_remove_house_data(self):
        self.homes = Homes()
        self.homes.add_address("4544 Radnor St")
        self.homes.add_address("834 N Museo Drive")
        self.homes.add_address("1903 N Willow Rd")
        assert len(self.homes.house_data) == 3
        self.homes.remove_house_data("4544 Radnor")
        assert len(self.homes.house_data) == 2
        assert self.homes.remove_house_data("Non-existent house #1") == "There may have been a typo with the entered address"
        self.homes.remove_house_data("834 N Museo Dr")
        assert len(self.homes.house_data) == 1
        self.homes.remove_house_data("1903 N")
        assert self.homes.remove_house_data("Non-existent house #2") == "The dataframe is empty"
    
    
    def test_get_data(self):
        self.homes.add_info_from_address("4544 Radnor St")
        self.homes.add_info_from_address("834 N Museo Drive")
        self.homes.add_info_from_address("1903 N Willow Rd")
        df = self.homes.get_data()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        
        
    
    def test_get_reet(self):
        df = self.homes.get_reet()
        assert len(df) == 3
        self.homes.add_info_from_address("4544 Radnor Street")
        df = self.homes.get_reet()
        assert len(df) == 4
    
    def test_query_r(self):
        assert self.homes.query_r("random", "nonexistant") == "There was an issue with some of the data you entered"
        assert self.homes.query_r("address", "90210 Green Bay St") == "There were no results =("
        df = self.homes.query_r("address", "1903 N Willow Rd")
        assert len(df) == 1
        df = self.homes.query_r("address", "4544 Radnor St")
        assert len(df) == 2
    
    def test_query_h(self):
        assert self.homes.query_r("random", "nonexistant") == "There was an issue with some of the data you entered"
        assert self.homes.query_r("address", "90210 Green Bay St") == "There were no results =("
        
        df = self.homes.query_h("beds", "=4")
        assert len(df) == 2
        df = self.homes.query_r("address", "4544 Radnor St")
        assert len(df) == 2

    def test_remove_duplicates(self):
        self.homes.remove_duplicates()
        assert len(self.homes.house_data) == 3
        assert len(self.homes.house_data) == 3