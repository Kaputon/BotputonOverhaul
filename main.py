import discord
from discord.ext import commands, tasks
import os
import pymongo
from time import time as tick

intents = discord.Intents.default()
intents.members = True
intents.typing = True
intents.presences = True

bot = commands.Bot("~", intents=intents)

# Initializing some important variables.
DBurl = os.environ.get("URLstring")
cogs = ["botcogs."+cog[:-3] for cog in os.listdir("./botcogs") if cog[-3:] == ".py"]
cluster = pymongo.MongoClient(DBurl)
time_log = []
#-------]

@bot.event
async def on_ready():
    print("Bot is ready!")
    print("Loading cogs. . .")

    time_log.append(tick()) # Set up a base start time for the time log.

    # Load all of the cogs.
    for cog in cogs:
        try:
            bot.load_extension(cog)
            print(cog + " was loaded.")
        except Exception as e:
            print(e)

    # Begin the loop to shut off the database connection if too much time has passed.
    TimeSinceLastMSG.start()

@bot.event
async def on_message(ctx):
    global cluster
    time_log[0] = tick() # Log the time of each message.

    # If a connection is not open, open one.
    if not cluster:
        cluster = pymongo.MongoClient(DBurl)
    db = cluster["Botputon-Data"]
    serverdat = db["ServerData"]
    playerdat = db["UserData"]
    #-------]

    # If the server is not logged, begin logging it. Otherwise, add one to the server count.
    if not serverdat.find_one({"_id" : ctx.guild.id}):
        serverdat.insert_one({"_id" : ctx.guild.id,"name" : ctx.guild.name , "total-posts" : 0})
    else:
        serverdat.update_one({"_id" : ctx.guild.id}, {"$inc" : {"total-posts" : 1}})
    #-------]

    # Database filters and important variables.
    g_ID = str(ctx.guild.id)
    USER_FILT = {"_id" : ctx.author.id}
    SERV_FILT = {"_id" : ctx.author.id, f"{g_ID}" : {"$exists" : True} }
    #------]

    # If the player is not in the database, put them in.
    if not playerdat.find_one(USER_FILT):
        playerdat.insert_one({"_id" : ctx.author.id,"name" : ctx.author.name, f"{g_ID}" : 0})
    # ...if they're in the database, but the server isn't, add the server to their id.
    elif playerdat.find_one(USER_FILT) and not playerdat.find_one(SERV_FILT):
        print("Not found")
        playerdat.update_one(USER_FILT, {"$set" : {g_ID : 1}})
    # If the player and server exist, add 1 post to their ID
    if playerdat.find_one(SERV_FILT):
        print("Found")
        playerdat.update_one(USER_FILT, {"$inc" : {g_ID : 1} } )
    await bot.process_commands(message)


@tasks.loop(seconds=300) # 5 minutes
async def TimeSinceLastMSG():
    global cluster
    # If it has been more than 2 minutes since the last message, and cluster is open, close it.
    if abs(tick() - time_log[0]) >= 120 and cluster:
        print("Closing Database connection")
        cluster.close()
        cluster = False



token = os.environ.get("TOKEN")
bot.run(token)
