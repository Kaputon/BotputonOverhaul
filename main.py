import discord
from discord.ext import commands
import os
import boto3

intents = discord.Intents.default()
intents.members = True
intents.typing = True
intents.presences = True

bot = commands.Bot("~", intents=intents)

cogs = ["botcogs."+cog[:-3] for cog in os.listdir("./botcogs") if cog[-3:] == ".py"]

@bot.event
async def on_ready():
    print("Bot is ready!")
    print("Loading cogs. . .")
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(cog + " was loaded.")
        except Exception as e:
            print(e)

TOKEN = boto3.resource('TOKEN')
bot.run(TOKEN)
