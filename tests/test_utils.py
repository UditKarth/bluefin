from src.utils import *



def test_get_info_from_address():
    assert get_info_from_address("123 Nonsense Street") == "There was an issue with the entered address"
    assert get_info_from_address("") == "There was an issue with the entered address"
    assert get_info_from_address("4544 Radnor Street") == {'address': '4544 Radnor St',
 'city': 'Detroit',
 'state': 'MI',
 'zip_code': '48224',
 'beds': 4,
 'baths': 2.0,
 'zestimate': '$58,317 (+$28K since last sold)',
 'og_price': 30000,
 'sq_ft': 656,
 'parking': '1',
 'lot_size': '4,356',
 'parking_type': 'Detached Garage',
 'home_type': 'Single Family'}
    assert get_info_from_address("834 N Museo Drive") == {'address': '834 N Museo Dr',
 'city': 'Mountain House',
 'state': 'CA',
 'zip_code': '95391',
 'beds': 3,
 'baths': 2.5,
 'zestimate': '$910,349', #Zestimate values can change; check if the only difference in the assertion is zestimate 
 'og_price': 'N/A',
 'sq_ft': 2111,
 'parking': '2',
 'lot_size': '6,637',
 'parking_type': None,
 'home_type': 'New'}
    get_closest_loan_term

def test_get_closest_loan_term():
    assert get_closest_loan_term(100) == 'thirtyYearFixed'
    assert get_closest_loan_term(0) == 'fifteenYearFixed'
    assert get_closest_loan_term(19) == 'twentyYearFixed'
    assert get_closest_loan_term(16) == 'fifteenYearFixed'
    assert get_closest_loan_term(21) == 'twentyYearFixed'
    assert get_closest_loan_term(26) == 'thirtyYearFixed'
    
