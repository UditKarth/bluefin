from src.house import *
class TestHouse:
    def setup_class(cls):
        """Called before every class intialization"""
        """Made so that the following three house objects can be used for testing"""
        # test_house_1 = get_info_from_address("123 Nonsense Court")
        # test_house_2 = get_info_from_address("34 Matrix Ct")
        # test_house_3 = get_info_from_address("4544 Radnor Street, Detroit, MI")
        pass
    
    def teardown_class(cls):
        """Called after every class initialization"""
        """"Remove the intial 3 house objects"""
        pass

    def setup_method(self):
        pass

    def teardown_method(self):
        pass

    def test_detailed(self):
        house = House()
        house.street_address = "123 Main St"
        house.city = "Exampleville"
        house.state = "Exampleria"
        house.zip_code = "12345"
        house.beds = 3
        house.baths = 2
        house.sq_ft = 1500
        house.parking = 2
        house.parking_type = "Garage"
        house.lot_size = 0.25
        house.home_type = "Single Family"
        house.zestimate = "$300,000"
        house.og_price = "$250,000"

        detailed_string = house.detailed
        expected_string = """Address: 123 Main St Exampleville, Exampleria 12345
        Home Type: Single Family
        Beds: 3
        Baths: 2
        SqFt: 1500
        Lot Size: 0.25
        Zestimate: $300,000
        Last Selling Price: $250,000
        Parking Spaces: 2
        Parking Type: Garage"""
        assert detailed_string.strip() == expected_string.strip()
        
        house.street_address = "456 South Main Avenue"
        house.city= "Example Town"
        house.state = "Exampleria" 
        house.zip_code = "12345"
        house.parking = None
        house.og_price = "N/A"
        detailed_string = house.detailed
        expected_string = """Address: 456 South Main Avenue Example Town, Exampleria 12345
        Home Type: Single Family
        Beds: 3
        Baths: 2
        SqFt: 1500
        Lot Size: 0.25
        Zestimate: $300,000
        Last Selling Price: N/A
        Parking Spaces: None
        Parking Type: Garage"""
        assert detailed_string == expected_string

        new_house = House()
        assert new_house.detailed == "There is no data for this house"

    def test_from_dict(self):
        house_dict = {
            'address': "123 Main St",
            'city': "Exampleville",
            'state': "Exampleria",
            'zip_code': "12345",
            'beds': 3,
            'baths': 2,
            'zestimate': "$300,000",
            'og_price': "$250,000",
            'parking': 2,
            'parking_type': "Garage",
            'sq_ft': 1500,
            'lot_size': 0.25,
            'home_type': "Single Family"
        }
        house = House()
        house = house.from_dict(house_dict)

        assert (house.street_address == "123 Main St")
        assert (house.city == "Exampleville")
        assert (house.state == "Exampleria")
        assert(house.zip_code == "12345")
        assert(house.beds == 3)
        assert (house.baths == 2)
        assert (house.zestimate == "$300,000")
        assert (house.og_price == "$250,000")
        assert (house.parking == 2)
        assert (house.parking_type == "Garage")
        assert (house.sq_ft == 1500)
        assert (house.lot_size == 0.25)
        assert (house.home_type == "Single Family")

        house_dict = {
            'address': "123 Main St",
            'Color': "Green",
            'state': "Exampleria",
            'zip_code': "12345",
            'beds': 3,
            'baths': 2,
            'zestimate': "$300,000",
            'last_price': "$250,000",
            'parking': 2,
            'parking_type': "Garage",
            'sq_ft': 1500,
            'lot_size': 0.25,
            'home_type': "Single Family"
        }
        assert house.from_dict(house_dict) == None

        house_dict = {
            'address': "123 Main St",
            'zip_code': "12345",
            'beds': 3,
            'baths': 2,
            'zestimate': "$300,000",
            'last_price': "$250,000",
            'parking': 2,
            'parking_type': "Garage",
            'sq_ft': 1500,
            'lot_size': 0.25,
            'home_type': "Single Family"
        }
        assert house.from_dict(house_dict) == None
        
        new_dict = get_info_from_address("4544 Radnor Street")
        new_house = House()
        new_house = new_house.from_dict(new_dict)
        
        assert (new_house.street_address == '4544 Radnor St')
        assert (new_house.city == 'Detroit')
        assert (new_house.state == 'MI')
        assert(new_house.zip_code == '48224')
        assert(new_house.beds == 4)
        assert (new_house.baths == 2.0)
        assert (new_house.zestimate == '$58,317 (+$28K since last sold)')
        assert (new_house.og_price == 30000)
        assert (new_house.parking == "1")
        assert (new_house.parking_type == "Detached Garage")
        assert (new_house.sq_ft == 656)
        assert new_house.lot_size == "4,356"
        assert (new_house.home_type == "Single Family")

    def test_as_dict(self):
        house = House()
        house.street_address = "123 Main St"
        house.city = "Exampleville"
        house.state = "Exampleria"
        house.zip_code = "12345"
        house.beds = 3
        house.baths = 2
        house.sq_ft = 1500
        house.parking = 2
        house.parking_type = "Garage"
        house.lot_size = 0.25
        house.home_type = "Single Family"
        house.zestimate = "$300,000"
        house.og_price = "$250,000"

        house_dict = house.as_dict()

        expected_dict = {
            'address': "123 Main St",
            'city': "Exampleville",
            'state': "Exampleria",
            'zip_code': "12345",
            'beds': 3,
            'baths': 2,
            'zestimate': "$300,000",
            'last_price': "$250,000",
            'parking': 2,
            'parking_type': "Garage",
            'sq_ft': 1500,
            'lot_size': 0.25,
            'home_type': "Single Family"
        }
        assert house_dict == expected_dict

        
        house.parking_type = None
        house.home_type = "New"
        expected_dict = {
            'address': "123 Main St",
            'city': "Exampleville",
            'state': "Exampleria",
            'zip_code': "12345",
            'beds': 3,
            'baths': 2,
            'zestimate': "$300,000",
            'last_price': "$250,000",
            'parking': 2,
            'parking_type': None,
            'sq_ft': 1500,
            'lot_size': 0.25,
            'home_type': "New"
        }
        assert house.as_dict() == expected_dict
        new_house = House()
        assert new_house.detailed == "There is no data for this house"
      