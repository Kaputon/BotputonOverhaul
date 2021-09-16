import discord
from discord.ext import commands
from botConfig import get_blacklisted_channels as blacklist # Import our config file and get the blacklisted text channels


class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx):
        members = {mem.name: [0, mem.id] for mem in ctx.guild.members if not mem.bot} # Create a dictionary with the members name for the key, and a list with...
                                                                                      # their post count and ID for the value. Only add if they're not a bot.
        channels = [chan for chan in ctx.guild.text_channels if not (chan.name in blacklist())] # Grab the channels which are not in the blacklist.

        async with ctx.typing():
            for chan in channels: # For each message in each channel, check if the author is in the dictionary, if they are, increase post count.
                async for message in chan.history(limit=None):
                    try:
                        members[message.author.name][0] += 1
                    except Exception:
                        continue

        embed = discord.Embed(title="Post Leaderboard")
        embed.set_author(name="Ranks everyone in the server by post amount.", icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Bots excluded.", icon_url=self.bot.user.avatar_url)
        x = 1
        top = None
        for key, value in sorted(members.items(), key=lambda z: members.values(), reverse=True): # Iterate through a dictionary sorted by the members values.
            if x == 1: # If this member is the top poster, set the top variable to his avatar for future thumbnail usage.
                top = str(self.bot.get_user(value[1]).avatar_url)
            if x >= 10: # Break the loop at 10 users. 
                break
            embed.add_field(name=str(x) + f". {key}",
                            value=f"{value[0]} posts",
                            inline=False)
            x += 1

        embed.set_thumbnail(url=top)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
