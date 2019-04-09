import stocks
import news
import agent
import discord
from discord.ext import commands

stock_market = None

news_count = 4

def init():
  global stock_market
  news.load_news()

  stock_market = stocks.gen_stock_market(news_count) # initialises stock prices

def tick():
  global stock_market
  stock_market.tick() # completes a turn

# bot

token = "NTYyMzE4NDU3Nzk5MDQ5MjM2.XKUasg.gISU0p7dmxfwMvDkYzXLbGjV2Bg"

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
  init()

# clears a channel of messages (for refreshing news/stocks/balances)
async def clear(channel):
  async for msg in client.logs_from(channel):
    await client.delete_message(msg)

# template
@client.command(pass_context = True)
async def test(ctx):
  await client.send_message(ctx.message.channel, "Hello")

# set change multiplier - changes how much stocks fluctuate from news
@client.command(pass_context = True)
async def setcm(ctx, val):
  if not ctx.message.author.server_permissions.administrator:
    return
  news.change_mul = float(val)

# re-initialises the stock market
@client.command(pass_context = True)
async def reset(ctx):
  if not ctx.message.author.server_permissions.administrator: # only for admins
    return
  init()

# sets self to afk
@client.command(pass_context = True)
async def afk(ctx):
  stock_market.afk_agent(ctx.message.author.id, True)

# sets self to not afk
@client.command(pass_context = True)
async def unafk(ctx):
  stock_market.afk_agent(ctx.message.author.id, False)

# set other user to afk by user id
@client.command(pass_context = True)
async def setafk(ctx, name):
  if not ctx.message.author.server_permissions.administrator:
    return
  stock_market.afk_agent(name, True)

# set other user to not afk by user id
@client.command(pass_context = True)
async def setunafk(ctx, name):
  if not ctx.message.author.server_permissions.administrator:
    return
  stock_market.afk_agent(name, True)

# buy a stock
@client.command(pass_context = True)
async def buy(ctx, stock, amount):
  amount = int(amount)
  if stock in stocks.stock_data.keys(): # if they entered a valid stock
    bal = stock_market.get_agent_balance(ctx.message.author.id)
    if bal >= stock_market.stock_prices[stock] * amount: # if they have enough money
      stock_market.buy(ctx.message.author.id, stock.lower(), amount) # process purchase
      await balance_redisplay() # refresh balance listings
      await display_stocks(ctx.message.channel, ctx.message.author.id) # display users stocks
      await client.send_message(ctx.message.channel, "Done")
    else:
      await client.send_message(ctx.message.channel, "Not enough money, need " + str(stock_market.stock_prices[stock] * amount) + ", but only have " + str(bal))
  else:
    await client.send_message(ctx.message.channel, "Invalid stock name")

# sell ALL stocks of a user
@client.command(pass_context = True)
async def sellall(ctx):
  for i in range(0, len(stocks.stock_data)):
    stock_name = list(stocks.stock_data.keys())[i]
    tmp = stock_market.get_agent_stock(ctx.message.author.id, stock_name)
    if tmp > 0:
      # dont display when selling individual stocks
      await sell_stock(ctx, stock_name, tmp, display = False) # only sell stocks which the user owns
  await balance_redisplay() # refresh balance listings
  await display_stocks(ctx.message.channel, ctx.message.author.id)
  await client.send_message(ctx.message.channel, "Done")

# command to sell amount of stock
@client.command(pass_context = True)
async def sell(ctx, stock, amount):
  amount = int(amount)
  await sell_stock(ctx, stock, amount)

# function to sell amount of stock
async def sell_stock(ctx, stock, amount, display = True):
  if stock in stocks.stock_data.keys():
    u_amount = stock_market.get_agent_stock(ctx.message.author.id, stock)
    if u_amount >= amount:
      stock_market.sell(ctx.message.author.id, stock.lower(), amount)
      if display:
        await balance_redisplay() # refresh balance lsitings
        await display_stocks(ctx.message.channel, ctx.message.author.id) # display users stocks
        await client.send_message(ctx.message.channel, "Done")
    else:
      if display:
        await client.send_message(ctx.message.channel, "Not enough of that stock, only have " + str(u_amount))
  else:
    if display:
      await client.send_message(ctx.message.channel, "Invalid stock name")

# display stocks of a user
async def display_stocks(channel, name):
  await client.send_message(channel, stock_market.get_agent_stock_str(name))

# command to display own stocks
@client.command(pass_context = True)
async def mystocks(ctx):
  await display_stocks(ctx.message.channel, ctx.message.author.id)

# initialises users and their balances
@client.command(pass_context = True)
async def init_balances(ctx, start_balance):
  start_balance = int(start_balance)
  if not ctx.message.author.server_permissions.administrator: # only for admins, otherwise exit
    return
  users = ctx.message.server.members # get list of users
  stock_market.agents = []
  for user in users:
    if user.id != "562318457799049236": # (id of the bot)
      stock_market.add_agent(agent.Agent(str(user.id), start_balance, user.name)) # add agent object for each user

  await tick_redisplay() # initial news and stock display
  await client.send_message(ctx.message.channel, "Done")
  
@client.command(pass_context = True)
async def bals(ctx): # display balances
  await balance_redisplay()

@client.command(pass_context = True)
async def mybal(ctx): # display balances
  await client.send_message(ctx.message.channel, str(stock_market.get_agent_balance(ctx.message.author.id)))

# refresh balances
async def balance_redisplay():
  bal_channel = client.get_channel("563430326626549781") # (id of balance channel)
  await clear(bal_channel) # clear channel before displaying
  string = ""
  for agent in stock_market.agents:
    string += agent.display_name + ": " + str(agent.balance) + " (" + str(stock_market.get_total_value(agent.owned_stocks) + agent.balance) + ")\n"
  await client.send_message(bal_channel, string) # send string of all balances

# refresh all displays
async def tick_redisplay():
  news_channel = client.get_channel("562315190134112265")
  await clear(news_channel)
  await client.send_message(news_channel, stock_market.get_news_str())

  stock_channel = client.get_channel("562315725465976832")
  await clear(stock_channel)
  await client.send_message(stock_channel, stock_market.get_stock_str())

  await balance_redisplay()
  
# admin command to do next tick
@client.command(pass_context = True)
async def tick(ctx):
  if not ctx.message.author.server_permissions.administrator:
    return
  stock_market.tick() # process
  await tick_redisplay() # refresh
  #await client.send_message(ctx.message.channel, "Next turn @everyone")

# user command to ready for next turn
@client.command(pass_context = True)
async def ready(ctx):
  await client.send_message(ctx.message.channel, "Readied")
  if stock_market.ready_agent(ctx.message.author.id, True): # returns true if all users are ready
    await tick_redisplay() # refresh displays for next turn
    await client.send_message(ctx.message.channel, "Next turn @everyone")

# user command to unready
@client.command(pass_context = True)
async def unready(ctx):
  await client.send_message(ctx.message.channel, "Unreadied")
  stock_market.ready_agent(ctx.message.author.id, False) # set user unready status
  
@client.command(pass_context = True)
async def du(ctx): # display unreadied
  string = "Unreadied:\n"
  for agent in stock_market.agents:
    if not (agent.ready or agent.is_afk): # dont display if ready or afk
      string += agent.display_name + "\n"
  await client.send_message(ctx.message.channel, string)

client.run(token) # runs the bot
