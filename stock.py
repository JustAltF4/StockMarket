
RAND_FLUCT_MIN = 0.97
RAND_FLUCT_MAX = 1.03

# stock class
class Stock():
  def __init__(self, name, price, stock_type, country):
    self.name = name
    self.price = price
    self.stock_type = stock_type
    self.country = country
    
  def tick(self):
    self.price *= random.uniform(RAND_FLUCT_MIN, RAND_FLUCT_MAX)
    self.price = round(self.price)
    if self.price <= 0:
      self.price = 1
    
