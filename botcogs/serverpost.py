import discord
from discord.ext import commands
import MongoHandler

class ServerPost(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def serverpost(self, ctx):

        g_ID = ctx.guild.id
        mongClient = MongoHandler.ClientMongo()

        embed = discord.Embed(title="Overall Posts", description=f"{mongClient.returnServer(g_ID)} posts.")
        embed.set_author(icon_url=self.bot.user.avatar_url, name=ctx.guild.name)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ServerPost(bot))
