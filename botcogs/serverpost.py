import discord
from discord.ext import commands

class ServerPost(commands.Cog):

    def __init__(self,bot):
        self.bot = bot

    @commands.command()
    async def serverpost(self, ctx, *args:str):
        channels = [ch for ch in ctx.guild.text_channels if not ch.name in args] # Grab each channel in the server if not blacklisted by the user.

        count = 0
        try:
            with ctx.typing():
                for chan in channels: # For each message in each channel, increase the count.
                    async for _ in chan.history(limit=None):
                        count+=1
            embed = discord.Embed(title="Overall Posts", description=f"{count} posts.")
            embed.set_author(icon_url=self.bot.user.avatar_url, name=ctx.guild.name)
            embed.set_thumbnail(url=ctx.guild.icon_url)
            await ctx.send(embed=embed) # Send it.
        except Exception as e:
            await ctx.send(e)

def setup(bot):
    bot.add_cog(ServerPost(bot))
    
