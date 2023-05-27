#DEPRECATED CLASS: NO LONGER USED


# from .house import *

# class Listing:
#     """
#     Listing class
#     """

#     def __init__(
#         self,
#         house=None,
#         list_price=None,
#         zestimate=None,
#         days_on_market=None,
#         original_list_price=None,
#         status=None,
#         mls_id=None,
#         open_house_date=None,
#         open_house_start_time=None,
#         open_house_end_time=None
#     ):
#         self.house = house
#         self.list_price = self._convert_to_numeric(list_price)
#         self.zestimate = self._convert_to_numeric(zestimate)
#         self.days_on_market = self._convert_to_numeric(days_on_market)
#         self.original_list_price = self._convert_to_numeric(original_list_price)
#         self.status = status
#         self.mls_id = mls_id
#         self.open_house_date = open_house_date
#         self.open_house_start_time = open_house_start_time
#         self.open_house_end_time = open_house_end_time

#     def __repr__(self):
#         return f"Address: {self.house} - List Price: {self.list_price} - Zestimate: {self.zestimate}"

#     @property
#     def detailed(self):
#         detail_string = "House Details:\n{house_details}\nStatus: {status}\nList Price: {list_price}\nZestimate: {zestimate}\nMLS ID: {mls_id}\nDays on Market: {days_on_market}\nOriginal Price: {original_list_price}\nOpen House: {open_house_date} - {open_house_start_time} to {open_house_end_time}\n\n"
#         return detail_string.format(
#             house_details=self.house.detailed,
#             status=self.status,
#             list_price=self.list_price,
#             zestimate=self.zestimate,
#             mls_id=self.mls_id,
#             days_on_market=self.days_on_market,
#             original_list_price=self.original_list_price,
#             open_house_date=self.open_house_date,
#             open_house_start_time=self.open_house_start_time,
#             open_house_end_time=self.open_house_end_time
#         )

#     def _convert_to_numeric(self, value):
#         if isinstance(value, (int, float)):
#             return value
#         try:
#             return float(value)
#         except (TypeError, ValueError):
#             return None

#     @property
#     def house(self):
#         return self._house

#     @house.setter
#     def house(self, house):
#         self._house = house

#     @property
#     def list_price(self):
#         return self._list_price

#     @list_price.setter
#     def list_price(self, list_price):
#         self._list_price = list_price

#     @property
#     def zestimate(self):
#         return self._zestimate

#     @zestimate.setter
#     def zestimate(self, zestimate):
#         self._zestimate = zestimate

#     @property
#     def days_on_market(self):
#         return self._days_on_market

#     @days_on_market.setter
#     def days_on_market(self, days_on_market):
#         self._days_on_market = days_on_market

#     @property
#     def original_list_price(self):
#         return self._original_list_price

#     @original_list_price.setter
#     def original_list_price(self, original_list_price):
#         self._original_list_price = original_list_price

#     @property
#     def status(self):
#         return self._status

#     @status.setter
#     def status(self, status):
#         self._status = status

#     @property
#     def mls_id(self):
#         return self._mls_id

#     @mls_id.setter
#     def mls_id(self, mls_id):
#         self._mls_id = mls_id

#     @property
#     def open_house_date(self):
#         return self._open_house_date

#     @open_house_date.setter
#     def open_house_date(self, open_house_date):
#         self._open_house_date = open_house_date

#     @property
#     def open_house_start_time(self):
#         return self._open_house_start_time

#     @open_house_start_time.setter
#     def open_house_start_time(self, open_house_start_time):
#         self._open_house_start_time = open_house_start_time

#     @property
#     def open_house_end_time(self):
#         return self._open_house_end_time

#     @open_house_end_time.setter
#     def open_house_end_time(self, open_house_end_time):
#         self._open_house_end_time = open_house_end_time

#     @property
#     def hsh(self):
#         return self.house.hsh

#     @classmethod
#     def from_dict(cls, dictionary):
#         try:
#             h = House.from_dict(dictionary['house'])
#             return cls(
#                 house=h,
#                 list_price=dictionary['list_price'],
#                 zestimate=dictionary['zestimate'],
#                 days_on_market=dictionary['days_on_market'],
#                 original_list_price=dictionary['original_list_price'],
#                 status=dictionary['status'],
#                 mls_id=dictionary['mls_id'],
#                 open_house_date=dictionary['open_house_date'],
#                 open_house_start_time=dictionary['open_house_start_time'],
#                 open_house_end_time=dictionary['open_house_end_time']
#             )
#         except (KeyError, TypeError):
#             return cls()

#     def as_dict(self):
#         d = {
#             'house': self.house.as_dict(),
#             'list_price': self.list_price,
#             'zestimate': self.zestimate,
#             'days_on_market': self.days_on_market,
#             'original_list_price': self.original_list_price,
#             'status': self.status,
#             'mls_id': self.mls_id,
#             'open_house_date': self.open_house_date,
#             'open_house_start_time': self.open_house_start_time,
#             'open_house_end_time': self.open_house_end_time
#         }
#         return d
#     def matches_search(
#         self,
#         house=None,
#         list_price=None,
#         zestimate=None,
#         days_on_market=None,
#         status=None
#     ):
#         if (
#             (list_price is None or self.list_price <= list_price) and
#             (zestimate is None or self.zestimate <= zestimate) and
#             (days_on_market is None or self.days_on_market <= days_on_market)
#         ):
#             if status is not None and self.status != status:
#                 return False
#             return True
#         return False

#     def as_html(self):
#         html_string = "<tr>"
#         for key in self.as_dict():
#             if key == 'house':
#                 h = House.from_dict(self.as_dict()[key])
#                 for key2 in h.as_dict():
#                     html_string += "<td>%s</td>" % (h.as_dict()[key2])
#             else:
#                 html_string += "<td>%s</td>" % (self.as_dict()[key])
#         html_string += "</tr>"
#         return html_string

#     def html_headers(self):
#         html_string = "<tr>"
#         for key in self.as_dict():
#             if key == 'house':
#                 h = House.from_dict(self.as_dict()[key])
#                 for key2 in h.as_dict():
#                     html_string += "<th>%s</th>" % (key2)
#             else:
#                 html_string += "<th>%s</th>" % (key)
#         html_string += "</tr>"
#         return html_string
