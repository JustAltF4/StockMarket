import random
import math
import news
from agent import Agent

# initial price ranges
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

# generate values based on price ranges
def gen_stock_prices():
  stock_prices = {}
  for key, v_range in stock_data.items():
    stock_prices[key] = random.choice(v_range)
  return stock_prices

# helper to initialise a stock market object
def gen_stock_market(news_count):
  return StockMarket(gen_stock_prices(), news.gen_country_multipliers(), news_count)

RAND_FLUCT_MIN = 0.9 # random range in which stock prices fluctuate each tick
RAND_FLUCT_MAX = 1.1

# stock market object - basically stores everything
class StockMarket():
  def __init__(self, stock_prices, country_multipliers, news_count, agents = [], start_add_news = True, tick_on_ready = True):
    self.stock_prices = stock_prices
    self.last_stock_prices = stock_prices
    self.country_multipliers = country_multipliers
    self.current_news = [] # news instances currently in use
    self.unused_news = [] # list of [name, country] of unused news stories
    self.used_news = [] # list of [name, country] of used news stories
    for news_name in news.news_objects.keys():
      # if a country is forced for the news story, creates as many copies as there are countries
      # to make the probability of it coming up equal to other stories
      if news.news_objects[news_name].force_country and not news.news_objects[news_name].is_sequel:
        for country in news.country_data.keys(): # create n duplicates
          self.unused_news.append([news_name, news.news_objects[news_name].force_country]) 
      else:
        for country in news.country_data.keys(): # create unused story definition for each country
          if not news.news_objects[news_name].is_sequel:
            self.unused_news.append([news_name, country])
    self.news_count = news_count
    self.add_news(news_count) # initialise news instances
    self.agents = agents
    self.tick_on_ready = tick_on_ready
    self.tick_counter = 0

  # returns total value of owned stocks based on stock prices
  def get_total_value(self, owned_stocks):
    return sum([
        v * self.stock_prices[k] for k, v in owned_stocks.items() 
      ])

  # process agent buying stock
  def buy(self, name, stock, amount):
    tmp = None
    for agent in self.agents:
      if agent.name == name: # find correct user
        tmp = agent
    if tmp == None: # if user does not exist, exit
      return
    tmp.owned_stocks[stock] += amount # add stock
    tmp.balance -= amount * self.stock_prices[stock] # take away from balance
  
  # process agent selling stock
  def sell(self, name, stock, amount):
    tmp = None
    for agent in self.agents:
      if agent.name == name: # find correct user
        tmp = agent
    if tmp == None: # if user does not exist, exit
      return
    tmp.owned_stocks[stock] -= amount # remove stock
    tmp.balance += amount * self.stock_prices[stock] # add balance

  # get list of stocks from specific agent
  def get_agent_stock_str(self, name):
    for agent in self.agents:
      if agent.name == name:
        return agent.get_stock_str()

  # get amount of stock owned by specific agent
  def get_agent_stock(self, name, stock):
    for agent in self.agents:
      if agent.name == name:
        return agent.owned_stocks[stock]

  # set agent afk status
  def afk_agent(self, name, value):
    for agent in self.agents:
      if agent.name == name:
        agent.is_afk = value
  
  # set agent ready status
  def ready_agent(self, name, value):
    unreadied = False
    for agent in self.agents:
      if agent.name == name:
        agent.ready = value
      if not (agent.ready or agent.is_afk):
        unreadied = True
    if not unreadied:
      self.tick() # tick if all are readied and return true 
      return True
    return False
  
  # find balance of specific agent
  def get_agent_balance(self, name):
    for agent in self.agents:
      if agent.name == name:
        return agent.balance
    return None

  # add agent to stock market agents
  def add_agent(self, agent):
    self.agents.append(agent)
    agent.owned_stocks = {key: 0 for key in stock_data.keys()}

  # fill news up to count
  def add_news(self, count):
    # while there are not enough unused news stories
    while len(self.unused_news) < self.news_count - len(self.current_news):
      idx = random.randrange(0, len(self.used_news)) # recycle used stories
      tmp = self.used_news.pop(idx)
      if "is_sequel" not in news.news_objects[tmp[0]]: # if the story is not a sequel
        self.unused_news.append(tmp)

    # fill up to count
    for i in range(len(self.current_news), self.news_count):
      tmp = [0, 0]
      if len(self.unused_news) > 0:
        idx = random.randrange(0, len(self.unused_news))
        tmp = self.unused_news.pop(idx) # take out random story
        tmp_idx = len(self.unused_news) - 1
        while tmp_idx >= 0:
          val = self.unused_news[tmp_idx]
          if tmp[0] == val[0] and tmp[1] == val[1]:
            self.unused_news.pop(tmp_idx) # remove all duplicates of selected story
          tmp_idx -= 1
        self.used_news.append(tmp) # add story to used news
      else:
        idx = random.randrange(0, len(self.used_news))
        tmp = self.used_news[idx] # choose from used news
        
      # create instance based on chosen news definition
      self.current_news.append(news.gen_instance(tmp[0], tmp[1]))

  # process tick
  def tick(self, add_more_news = True, unready_all = True):
    self.last_stock_prices = {k: v for k, v in self.stock_prices.items()} # duplicate stocks object
    tmp_news = self.current_news[:] # duplicate news
    self.current_news = []
    for news in tmp_news:
      self.stock_prices = news.execute(self.stock_prices, self.country_multipliers, self.current_news) # update stock prices based on news
    if add_more_news:
      self.add_news(self.news_count) # fill up news
    for name, price in self.stock_prices.items():
      self.stock_prices[name] = round(price * random.uniform(RAND_FLUCT_MIN, RAND_FLUCT_MAX)) # random fluctuations
      if self.stock_prices[name] == price:
        if random.uniform(0, 1) > 0.5:
          self.stock_prices[name] += 1
        else:
          self.stock_prices[name] -= 1 # small fluctuation if value is too small to be affected by percentage change
    if unready_all:
      for agent in self.agents:
        agent.ready = False # set agents to unready for next turn
    
    # make stocks come back to original values
    for name, value in self.stock_prices.items():
      if value not in stock_data[name]:
        middle = float(stock_data[name][0] + stock_data[name][-1]) / 2.0
        self.stock_prices[name] = round(value + (float(middle) - float(value)) * 0.225)
      if self.stock_prices[name] <= 0: # make sure stocks arent 0 or negative
        self.stock_prices[name] = 1

    self.tick_counter += 1 # increase turn counter
   
  # get string for news stories
  def get_news_str(self):
    output = "\n**News stories:**\n"
    for news in self.current_news:
      output += news.get_str() + "\n"
    return output

  # get string for stock prices
  def get_stock_str(self):
    output = "Turn: " + str(self.tick_counter) + "\n**Stock prices:**\n"
    for name, value in self.stock_prices.items():
      change = value - self.last_stock_prices[name]
      output += name.capitalize() + ": " + str(value) + "(" + ("+" if change >= 0 else "") + str(change) + ")\n"
    return output
