import discord
from discord.ext import commands
from botConfig import Assets


class StrawPoll(commands.Cog):
    img = Assets.StrawPollIMG

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def strawpoll(self, ctx, question: str, *args):
        EMOJIS = ["🇦", "🇧", "🇨", "🇩"]
        CHOICE_LETTERS = ["A","B","C","D"]
        ch_num = len(args)
        if (ch_num > 4) or (ch_num < 1):
            await ctx.send("You must have between one and four choices.", delete_after=10)
            return
        else:
            async with ctx.typing():
                embed = discord.Embed(title="```Question``` : ", description=f"*{question}*")
                embed.set_author(icon_url=ctx.message.author.avatar_url, name="STRAWPOLL")
                embed.set_footer(text="Make your voice heard.", icon_url=self.bot.user.avatar_url)
                embed.set_thumbnail(url=self.img)
                for field in range(0, ch_num):
                    embed.add_field(name=f"{CHOICE_LETTERS[field]})", value=f"{args[field]}", inline=True)
                msg = await ctx.send(embed=embed)
                for em in range(0, ch_num):
                    await msg.add_reaction(EMOJIS[em])
                return


def setup(bot):
    bot.add_cog(StrawPoll(bot))
