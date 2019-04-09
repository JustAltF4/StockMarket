import random
import json
import math

RAND_CHANGE_MIN = 0.9 # random range for price change when executing news
RAND_CHANGE_MAX = 1.1

change_mul = 0.35

# initial importance ranges - how much news affects prices
country_data = {
  "usa": (1.25, 1.3),
  "russia": (1.1, 1.15),
  "germany": (1, 1.1),
  "france": (0.95, 1.1),
  "uk": (0.95, 1.05),
  "mexico": (0.75, 0.85),
  "ethiopia": (0.5, 0.7),
}

# initialises importance values from ranges
def gen_country_multipliers():
  country_multipliers = {}
  for country, v_tuple in country_data.items():
    country_multipliers[country] = random.uniform(v_tuple[0], v_tuple[1])
  return country_multipliers

# template objects for news before creating instances
news_objects = {}

# creates news instance from news template
def gen_instance(news_name, country = random.choice(list(country_data.keys()))):
  return NewsInstance(news_objects[news_name], country)

# converts JSON into news object
def gen_news(row_data, full_data):
  tmp_news = News(row_data["info"], row_data["prices"], is_sequel = "is_sequel" in row_data)
  if "country" in row_data.keys(): # forced country
    tmp_news.force_country = row_data["country"]
  if "sequels" in row_data.keys(): # news stories that occur after
    tmp_news.sequels = row_data["sequels"]
  return tmp_news

# load all JSON into objects
def load_news():
  # load json data
  with open("news.json", "r") as read_file:
    news_data = json.loads(read_file.read())
  
  # convert to objects
  for name, data in news_data.items():
    news_objects[name] = gen_news(data, news_data)

# news instances include news and country / other data
class NewsInstance():
  def __init__(self, news, country):
    self.news = news
    if news.force_country:
      self.country = news.force_country
    else:
      self.country = country
  
  def get_str(self):
    return self.country.capitalize() + ": " + self.news.info

  def execute(self, stock_objects, country_multipliers, current_news):
    extremity = 1
    if self.country in country_multipliers.keys():
      extremity = country_multipliers[self.country] # default is 1, some countries are set to have specific importances
    return self.news.execute(stock_objects, extremity, current_news, self.country) # execute via template

# template objects
class News():
  def __init__(self, info, price_changes, is_sequel = False):
    self.info = info
    self.price_changes = price_changes
    self.sequels = []
    self.is_sequel = is_sequel
    self.force_country = False
  
  # takes and modifies stock prices
  def execute(self, stock_objects, extremity, current_news, country):
    for stock_object in stock_objects:
      # works out how to change stock prices
      if stock_object.stock_type not in self.price_changes.keys():
        continue
      tmp_mul = 1
      if country == stock_object.country:
        tmp_mul = 1.2
      mul = self.price_changes[stock_object.stock_type] ** (extremity * change_mul * tmp_mul * random.uniform(RAND_CHANGE_MIN, RAND_CHANGE_MAX))
      print(mul)
      stock_object.price *= mul  # modify stock prices
    if len(self.sequels) > 0: # if there are sequels
      name = self.sequels[random.randrange(0, len(self.sequels))]
      if name != "":
        current_news.append(gen_instance(name, country)) # adds a random sequel to the stock markets news
    return stock_objects
