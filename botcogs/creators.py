import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup as bs

img = "https://cdn.discordapp.com/attachments/389514146053488671/884939044037984266/ctf.png"
url = "https://creators.tf/servers?sort_by=online&method=DESC"


class Creators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def creators(self, ctx):
        players, map, connect_line, area = None, None, None, None

        server_list = []

        try:
            site = requests.get(url)
        except Exception as e:
            await ctx.send(e)

        if not site.status_code == 200:
            await ctx.send("An error occured with getting the website", delete_after=10)
            return

        soup = bs(site.text, 'html.parser')
        servers = soup.find_all('tr')[1:]

        for tag in servers:
            server = self.getimportant(tag)
            if not server:
                break
            server_list.append(server)

        sum = 0

        embed = discord.Embed(title="CREATORS.TF SERVERS - ")
        embed.set_image(url=img)

        for server in server_list:
            embed.add_field(name=f"{server[0]} | {server[1]} : ", value=f"{server[2]}/24 ; {server[3]}", inline=False)
            sum += int(server[2])

        embed.set_author(name="https://creators.tf/servers", icon_url=ctx.author.avatar_url)
        embed.set_footer(text=f"{sum} Concurrent Players on All Servers.", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed)

    def getimportant(self, tag):
        players, map, connect_line, area = 0, "NA", "NA", "Creators.TF"
        AREAS = ["West EU", "EU", "East US", "West US", "Australia", "Singapore", "Germany", "Seattle", "Poland",
                 "Events Silly Servers", "Balancemod.TF"]
        try:
            players = str(tag.find('label', class_="players-online").text).strip("\n")

            if int(players) == 0:
                return None

            map = str(tag.find('td', class_="server-list-col centered-text map-cover").text).strip("\n")
            area = str(tag.find('td', class_="server-list-col centered-text",
                                style="padding: 0 1rem").text).split("|")
            area = [location for location in area if location.strip().replace(" #1", "").replace(" #2", "").replace(" #3", "").replace(" #4", "") in AREAS][0]

            code = tag.find('td', class_="server-list-col flex")
            if code:
                try:
                    connect_line = str(code.find('a')['href']).strip("\n")
                except:
                    pass

            return [area, map, players, connect_line]
        except Exception as e:
            return False


def setup(bot):
    bot.add_cog(Creators(bot))
