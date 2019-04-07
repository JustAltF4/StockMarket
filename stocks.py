import random
import math
import news
from agent import Agent

stock_data = {
  "oil": range(14, 22),
  "electronics": range(6, 12),
  "meat": range(4, 14),
  "grain": range(4, 14),
  "water": range(8, 16),
  "steel": range(8, 18),
  "nuclear": range(2, 10),
  "coal": range(8, 16),
  "wine": range(4, 10),
  "arms": range(4, 8)
}

def gen_stock_prices():
  stock_prices = {}
  for key, v_range in stock_data.items():
    stock_prices[key] = random.choice(v_range)
  return stock_prices

def gen_stock_market(news_count):
  return StockMarket(gen_stock_prices(), news.gen_country_multipliers(), news_count)

RAND_FLUCT_MIN = 0.9
RAND_FLUCT_MAX = 1.1

class StockMarket():
  def __init__(self, stock_prices, country_multipliers, news_count, agents = [], start_add_news = True, tick_on_ready = True):
    self.stock_prices = stock_prices
    self.last_stock_prices = stock_prices
    self.country_multipliers = country_multipliers
    self.current_news = []
    self.unused_news = []
    self.used_news = []
    for news_name in news.news_objects.keys():
      if news.news_objects[news_name].force_country and not news.news_objects[news_name].is_sequel:
        for country in news.country_data.keys():
          self.unused_news.append([news_name, news.news_objects[news_name].force_country])
      else:
        for country in news.country_data.keys():
          if not news.news_objects[news_name].is_sequel:
            self.unused_news.append([news_name, country])
    self.news_count = news_count
    self.add_news(news_count)
    self.agents = agents
    self.tick_on_ready = tick_on_ready
    self.tick_counter = 0

  def get_total_value(self, owned_stocks):
    return sum([
        v * self.stock_prices[k] for k, v in owned_stocks.items()
      ])

  def buy(self, name, stock, amount):
    tmp = None
    for agent in self.agents:
      if agent.name == name:
        tmp = agent
    if tmp == None:
      return
    tmp.owned_stocks[stock] += amount
    tmp.balance -= amount * self.stock_prices[stock]
  
  def sell(self, name, stock, amount):
    tmp = None
    for agent in self.agents:
      if agent.name == name:
        tmp = agent
    if tmp == None:
      return
    tmp.owned_stocks[stock] -= amount
    tmp.balance += amount * self.stock_prices[stock]

  def get_agent_stock_str(self, name):
    for agent in self.agents:
      if agent.name == name:
        return agent.get_stock_str()

  def get_agent_stock(self, name, stock):
    for agent in self.agents:
      if agent.name == name:
        return agent.owned_stocks[stock]

  def afk_agent(self, name, value):
    for agent in self.agents:
      if agent.name == name:
        agent.is_afk = value

  def ready_agent(self, name, value):
    unreadied = False
    for agent in self.agents:
      if agent.name == name:
        agent.ready = value
      if not (agent.ready or agent.is_afk):
        unreadied = True
    if not unreadied:
      self.tick()
      return True
    return False

  def get_agent_balance(self, name):
    for agent in self.agents:
      if agent.name == name:
        return agent.balance
    return None

  def add_agent(self, agent):
    self.agents.append(agent)
    agent.owned_stocks = {key: 0 for key in stock_data.keys()}

  def add_news(self, count):
    while len(self.unused_news) < self.news_count - len(self.current_news):
      idx = random.randrange(0, len(self.used_news))
      tmp = self.used_news.pop(idx)
      if "is_sequel" not in news.news_objects[tmp[0]]:
        self.unused_news.append(tmp)

    for i in range(len(self.current_news), self.news_count):
      tmp = [0, 0]
      if len(self.unused_news) > 0:
        idx = random.randrange(0, len(self.unused_news))
        tmp = self.unused_news.pop(idx)
        tmp_idx = len(self.unused_news) - 1
        while tmp_idx >= 0:
          val = self.unused_news[tmp_idx]
          if tmp[0] == val[0] and tmp[1] == val[1]:
            self.unused_news.pop(tmp_idx)
          tmp_idx -= 1
        self.used_news.append(tmp)
      else:
        idx = random.randrange(0, len(self.used_news))
        tmp = self.used_news[idx]
      self.current_news.append(news.gen_instance(tmp[0], tmp[1]))

  def tick(self, add_more_news = True, unready_all = True):
    self.last_stock_prices = {k: v for k, v in self.stock_prices.items()}
    tmp_news = self.current_news[:]
    self.current_news = []
    for news in tmp_news:
      self.stock_prices = news.execute(self.stock_prices, self.country_multipliers, self.current_news)
    if add_more_news:
      self.add_news(self.news_count)
    for name, price in self.stock_prices.items():
      self.stock_prices[name] = round(price * random.uniform(RAND_FLUCT_MIN, RAND_FLUCT_MAX))
      if self.stock_prices[name] == price:
        if random.uniform(0, 1) > 0.5:
          self.stock_prices[name] += 1
        else:
          self.stock_prices[name] -= 1
    if unready_all:
      for agent in self.agents:
        agent.ready = False
    for name, value in self.stock_prices.items():
      if value not in stock_data[name]:
        middle = float(stock_data[name][0] + stock_data[name][-1]) / 2.0
        self.stock_prices[name] = round(value + (float(middle) - float(value)) * 0.1)
      if self.stock_prices[name] <= 0:
        self.stock_prices[name] = 1

    self.tick_counter += 1

  def get_news_str(self):
    output = "\n**News stories:**\n"
    for news in self.current_news:
      output += news.get_str() + "\n"
    return output

  def get_stock_str(self):
    output = "Turn: " + str(self.tick_counter) + "\n**Stock prices:**\n"
    for name, value in self.stock_prices.items():
      change = value - self.last_stock_prices[name]
      output += name.capitalize() + ": " + str(value) + "(" + ("+" if change >= 0 else "") + str(change) + ")\n"
    return output