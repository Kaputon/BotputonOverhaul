import discord
from discord.ext import commands
from botConfig import get_blacklisted_channels as blacklist


class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx):
        members = {mem.name: [0, mem.id] for mem in ctx.guild.members if not mem.bot}
        channels = [chan for chan in ctx.guild.text_channels if not (chan.name in blacklist())]

        async with ctx.typing():
            for chan in channels:
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
        for key, value in sorted(members.items(), key=lambda z: members.values(), reverse=True):
            if x == 1:
                top = str(self.bot.get_user(value[1]).avatar_url)
            if x >= 10:
                break
            embed.add_field(name=str(x) + f". {key}",
                            value=f"{value[0]} posts",
                            inline=False)
            x += 1

        embed.set_thumbnail(url=top)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
