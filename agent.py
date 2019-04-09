# 
# represents trading user
class Agent():
  def __init__(self, name, balance, display_name):
    self.name = name # discord user id
    self.balance = balance
    self.display_name = display_name # discord name
    self.ready = False
    self.owned_stocks = {} # how many of each stock the agent owns
    self.is_afk = False

  # display all owned stocks
  def get_stock_str(self):
    output = self.display_name + ":\n"
    for key, value in self.owned_stocks.items():
      if value > 0: # only display stocks if the agent owns some
        output += key.capitalize() + ": " + str(value) + "\n"
    return output
