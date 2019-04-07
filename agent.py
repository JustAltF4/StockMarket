
class Agent():
  def __init__(self, name, balance, display_name):
    self.name = name
    self.balance = balance
    self.display_name = display_name
    self.ready = False
    self.owned_stocks = {}
    self.is_afk = False

  def get_stock_str(self):
    output = self.display_name + ":\n"
    for key, value in self.owned_stocks.items():
      if value > 0:
        output += key.capitalize() + ": " + str(value) + "\n"
    return output
