import random

RAND_FLUCT_MIN = 0.97
RAND_FLUCT_MAX = 1.03

# stock class
class Stock():
  def __init__(self, name, price, stock_type, country):
    self.name = name
    self.price = price
    self.start_price = price
    self.stock_type = stock_type
    self.country = country
    
  def tick(self):
    self.price *= random.uniform(RAND_FLUCT_MIN, RAND_FLUCT_MAX)
    last_price = self.price
    last_start_price = self.start_price
    self.start_price += 0.1 * (last_price - last_start_price)
    self.price += 0.1 * (last_start_price - last_price)
    self.price = round(self.price)
    self.start_price = round(self.start_price)
    if self.price <= 0:
      self.price = 1
    
