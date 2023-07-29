import discord
from discord.ext import commands
import json
import os
# from game import Game, GameProcess
from process import *
import shutil
from test import Test
with open("./setting.json", mode = "rb") as file:
    data = file.read()
setting = json.loads(data)
token = setting["TOKEN"]
intents = discord.Intents(
    guilds = True, 
    # members = True, 
    voice_states = True, 
    messages = True, 
    reactions = True, 
    message_content = True
)
bot = commands.Bot(command_prefix="%", intents = intents)

@bot.event
async def on_ready():
    print(">> Bot is online <<")

@bot.command()
async def say_hi(ctx):
    await ctx.send("shut up")


@bot.command()
async def ping(ctx):
    await ctx.send(bot.latency)

@bot.command()
async def mjtest(ctx:commands.Context):
    await create_process(bot = bot, ctx = ctx)

@bot.command()
async def test(ctx):
    print(await Test(bot = bot))

if __name__=="__main__":
    bot.run(token)
