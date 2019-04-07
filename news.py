import random
import json
import math

RAND_MIN = 0.9
RAND_MAX = 1.1

change_mul = 1.5

country_data = {
  "usa": (1.2, 1.6),
  "russia": (1.1, 1.5),
  "germany": (1, 1.4),
  "france": (0.9, 1.3),
  "uk": (1.05, 1.35),
  "mexico": (0.4, 0.6),
  "ethiopia": (0.1, 0.3),
}

def gen_country_multipliers():
  country_multipliers = {}
  for country, v_tuple in country_data.items():
    country_multipliers[country] = random.uniform(v_tuple[0], v_tuple[1])
  return country_multipliers

news_objects = {}

def gen_instance(news_name, country = random.choice(list(country_data.keys()))):
  return NewsInstance(news_objects[news_name], country)

def gen_news(row_data, full_data):
  tmp_news = News(row_data["info"], row_data["prices"], is_sequel = "is_sequel" in row_data)
  if "country" in row_data.keys():
    tmp_news.force_country = row_data["country"]
  if "sequels" in row_data.keys():
    tmp_news.sequels = row_data["sequels"]
  return tmp_news

def load_news():
  with open("news.json", "r") as read_file:
    news_data = json.loads(read_file.read())
  
  for name, data in news_data.items():
    news_objects[name] = gen_news(data, news_data)

class NewsInstance():
  def __init__(self, news, country):
    self.news = news
    if news.force_country:
      self.country = news.force_country
    else:
      self.country = country
  
  def get_str(self):
    return self.country.capitalize() + ": " + self.news.info

  def execute(self, stock_prices, country_multipliers, current_news):
    extremity = 1
    if self.country in country_multipliers.keys():
      extremity = country_multipliers[self.country]
    return self.news.execute(stock_prices, extremity, current_news, self.country)

class News():
  def __init__(self, info, price_changes, is_sequel = False):
    self.info = info
    self.price_changes = price_changes
    self.sequels = []
    self.is_sequel = is_sequel
    self.force_country = False
  
  def execute(self, stock_prices, extremity, current_news, country):
    for stock, change in self.price_changes.items():
      mul = change ** (extremity * random.uniform(RAND_MIN, RAND_MAX) * change_mul)
      stock_prices[stock] = round(stock_prices[stock] * mul)
    if len(self.sequels) > 0:
      name = self.sequels[random.randrange(0, len(self.sequels))]
      if name != "":
        current_news.append(gen_instance(name, country))
    return stock_prices