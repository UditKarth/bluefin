from utils import *
from dataclasses import dataclass

@dataclass
class House:
    street_address: str = None
    city: str = None
    state: str = None
    zip_code: str = None
    beds: float = None
    baths: float = None
    sq_ft: float = None
    parking: float = None
    parking_type: str = None
    lot_size: float = None
    home_type: str = None
    zestimate: str = None
    og_price: str = None

    #Converts the house object to a string containing the address, city, state, and zip code
    def __repr__(self):
        return f"{self.street_address} {self.city}, {self.state} {self.zip_code}"

    @property

    #Returns a more detailed string containing the address, home type, beds, baths, sq ft, lot size, zestimate,
    #last selling price, parking spaces, and parking type
    def detailed(self):
        if self.street_address == None:
            return "There is no data for this house"
        detail_string = """Address: {address}
        Home Type: {home_type}
        Beds: {beds}
        Baths: {baths}
        SqFt: {sq_ft}
        Lot Size: {lot_size}
        Zestimate: {zestimate}
        Last Selling Price: {og_price}
        Parking Spaces: {parking}
        Parking Type: {parking_type}"""
        return detail_string.format(
            address=str(self),
            home_type=self.home_type,
            beds=self.beds,
            baths=self.baths,
            sq_ft=self.sq_ft,
            lot_size=self.lot_size,
            zestimate=self.zestimate,
            og_price=self.og_price,
            parking=self.parking,
            parking_type=self.parking_type
        )

    @property
    #returns a hexadecimal hash of the house object
    def hsh(self):
        m = hashlib.md5()
        m.update(str(self).encode())
        return m.hexdigest()

    @classmethod
    #creates a house object from a dictionary
    def from_dict(self, dictionary):
        try:
            self.street_address = dictionary['address']
            self.city = dictionary['city']
            self.state = dictionary['state']
            self.zip_code = dictionary['zip_code']
            self.beds = dictionary['beds']
            self.baths = dictionary['baths']
            self.zestimate = dictionary['zestimate']
            self.og_price = dictionary['og_price']
            self.parking = dictionary['parking']
            self.parking_type = dictionary['parking_type']
            self.sq_ft = dictionary['sq_ft']
            self.lot_size = dictionary['lot_size']
            self.home_type=dictionary['home_type']
            return self
        except:
            return None
        
    #returns a dictionary of the house object
    def as_dict(self):
        if self.street_address == None:
            return "There is no data for this house"
        return {
            'address': self.street_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'beds': self.beds,
            'baths': self.baths,
            'zestimate': self.zestimate,
            'last_price': self.og_price,
            'parking': self.parking,
            'parking_type': self.parking_type,
            'sq_ft': self.sq_ft,
            'lot_size': self.lot_size,
            'home_type': self.home_type
        }

#DEPRECATED: became useless with addition of Homes class
    # def matches_search(self, beds=None, baths=None, sq_ft=None, parking=None, lot_size=None, price=None):
    #     return (
    #         (beds is None or self.beds >= beds) and
    #         (baths is None or self.baths >= baths) and
    #         (sq_ft is None or self.sq_ft >= sq_ft) and
    #         (parking is None or self.parking >= parking) and
    #         (lot_size is None or self.lot_size >= lot_size) and 
    #         (price is None or self.zestimate <= price)
    #     )


