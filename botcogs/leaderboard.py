import discord
from discord.ext import commands
import MongoHandler

class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leaderboard(self, ctx):
        g_ID = ctx.guild.id
        mongClient = MongoHandler.ClientMongo()
        post_dictionary = mongClient.returnUser(g_ID)

        embed = discord.Embed(title="Post Leaderboard")
        embed.set_author(name="Ranks everyone in the server by post amount.", icon_url=ctx.author.avatar_url)
        embed.set_footer(text="Bots excluded.", icon_url=self.bot.user.avatar_url)

        x = 1
        top = None
        for key, value in sorted(post_dictionary.items(), key=lambda z: z[1], reverse=True):
            user = self.bot.get_user(key)
            if x == 1:
                top = str(user.avatar_url)
            if x >= 10:
                break
            embed.add_field(name=str(x) + f". {user.name}",
                            value=f"{value} posts",
                            inline=False)
            x += 1

        embed.set_thumbnail(url=top)
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Leaderboard(bot))
