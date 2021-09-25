import discord
from discord.ext import commands
import os
import MongoHandler as mongoH

intents = discord.Intents.default()
intents.members = True
intents.typing = True
intents.presences = True

bot = commands.Bot("~", intents=intents)

cogs = ["botcogs."+cog[:-3] for cog in os.listdir("./botcogs") if cog[-3:] == ".py"]

mongClient = mongoH.ClientMongo()

@bot.event
async def on_ready():
    print("Bot is ready!")
    print("Loading cogs. . .")

    # Load all of the cogs.
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(cog + " was loaded.")
        except Exception as e:
            print(e)

@bot.event
async def on_message(ctx):
    information = [[ctx.guild.id, ctx.guild.name], # Server info!
                   [ctx.author.id, ctx.author.name] # User info
                   ]

    global mongClient

    # On message, pass pertinent information to the Client Handler
    mongClient.handleServer(information[0])
    mongClient.handleUser(information[0][0] ,information[1])
    #----]

    await bot.process_commands(ctx)


TOKEN = os.environ.get("TOKEN")
bot.run(TOKEN)
