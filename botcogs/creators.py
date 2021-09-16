# This command uses requests and bs4 to access the Creators.TF website and returns the status of the servers.

import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup as bs

img = "https://cdn.discordapp.com/attachments/389514146053488671/884939044037984266/ctf.png" # Embed image
url = "https://creators.tf/servers?sort_by=online&method=DESC" # Creators.TF Servers list, sorted by player count for ease of access.


class Creators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def creators(self, ctx):
        players, map, connect_line, area = None, None, None, None # Prepare the four variables we will put in the embed.

        server_list = [] # List to hold each server as we iterate through available ones.
      
        try:
            site = requests.get(url)
        except Exception as e:
            await ctx.send(e)

        if not site.status_code == 200: # If site is not available, send error message and return.
            await ctx.send("An error occured with getting the website", delete_after=10)
            return

        soup = bs(site.text, 'html.parser')
        servers = soup.find_all('tr')[1:] # Get all the Creators.TF server rows, excluding the first tab, which is not a server.

        for tag in servers: # For child tags in each server row.
            server = self.getimportant(tag) # Hand off the tags to the handler function.
            if not server: # Servers are sorted by player count, if you hit zero, break to save time.
                break
            server_list.append(server) # Otherwise, add this server to the list.

        sum = 0

        embed = discord.Embed(title="CREATORS.TF SERVERS - ")
        embed.set_image(url=img)

        for server in server_list:
            embed.add_field(name=f"{server[0]} | {server[1]} : ", value=f"{server[2]}/24 ; {server[3]}", inline=False)
            sum += int(server[2]) # Add the players in each server continuously to get a rolling count.

        embed.set_author(name="https://creators.tf/servers", icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"{sum} Concurrent Players on All Servers.", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    def getimportant(self, tag):
        players, map, connect_line, area = 0, "NA", "NA", "NA" # Initialize the variables in case of failure.
        AREAS = ["West EU", "East US", "West US", "Australia", "Singapore", "Germany", "Seattle", "Poland"] # List of areas.
        try:
            players = str(tag.find('label', class_="players-online").text).strip("\n") # Grab the players

            if int(players) == 0: # If the players are 0, you've reached the end, break the loop and continue.
                return None

            map = str(tag.find('td', class_="server-list-col centered-text map-cover").text).strip("\n") # Grab the map.
            area = str(tag.find('td', class_="server-list-col centered-text",
                                style="padding: 0 1rem")).split("|") # Split the main text row by the '|' symbol
            
            area = [location for location in area if location.strip() in AREAS][0] # Iterate through each element, if it is in the list of areas, keep it.
                                                                                   # Then choose the first element, as there should only be one.

            code = tag.find('td', class_="server-list-col flex")
            if code:
                try:
                    connect_line = str(code.find('a')['href']).strip("\n") # Get the server connect hyperlink.
                except:
                    pass

            return [area, map, players, connect_line] # Return these four variables for embed preparation.
        
        except:
            return False


def setup(bot):
    bot.add_cog(Creators(bot))
