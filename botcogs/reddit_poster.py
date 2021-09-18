import discord
from discord.ext import commands, tasks
from time import time as tick
import asyncpraw
import os
from asyncio import sleep

WAIT_TIME = 5

class RedditPost(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ID = os.environ.get("reddit_id")
        self.SECRET = os.environ.get("reddit_secret")
        self.AGENT = os.environ.get("reddit_agent")
        self.PREV_POSTS = []
        self.POST_WAIT = 3600 * 4  # 4 hours
        self.PREV_C_ID = 888704383305515029
        self.JSON_ID = 888709799338975293
        self.thumb = "https://cdn.discordapp.com/attachments/389514146053488671/831620871210795079/reddit-logo-16.png"
        self.gatherPost.start()

    # Grab the timestamp of the previous post, if has been four hours since the last post, return True for preparing the post.
    async def checkStamp(self, channel):
        timestamp = [float(str(mess.content).split(" ")[1]) async for mess in channel.history(limit=1)][0]

        if abs(timestamp - tick()) >= self.POST_WAIT:
            return True
        else: # Otherwise, set the WAIT_TIME variable to the amount of time until the next post is ready.
            global WAIT_TIME
            WAIT_TIME = (timestamp + self.POST_WAIT) - tick()
            return False

    # Make sure the post is not stickied and the post has not been posted prior.
    async def checkPost(self, thread):
        if not thread.stickied and not (str(thread.author) == "exaflamer") and not (str(thread.url) in self.PREV_POSTS):
            return True
        return False


    @tasks.loop(seconds=5)
    async def gatherPost(self):

        json = self.bot.get_channel(self.JSON_ID)

        # Get the ID of the channel we will post the link to.
        POST_CHANNEL = self.bot.get_channel(
            [int(str(ID.content).split(" ")[1]) async for ID in json.history(limit=1)][0]
        )

        # Storage for all the previous Reddit posts. Poverty persistent data.
        PREV_CHANNEL = self.bot.get_channel(self.PREV_C_ID)

        # If the PREV_POSTS list does not contain anything, then gather up the PREV_CHANNEL urls.
        if len(self.PREV_POSTS) < 1:
            self.PREV_POSTS = [str(mess.content).split(" ")[0] async for mess in PREV_CHANNEL.history(limit=None)]

        post_dict = {
            "Upvotes": [],
            "Post Title": [],
            "Content": [],
            "Url": [],
            "Author": [],
        }

        redditAPI = asyncpraw.Reddit(
            client_id=self.ID,
            client_secret=self.SECRET,
            user_agent=self.AGENT,
        )
        sub = await redditAPI.subreddit("truetf2")

        if await self.checkStamp(PREV_CHANNEL) == True:
            async for post in sub.hot(limit=30):
                if not await self.checkPost(post):
                    continue
                else:
                    post_dict["Upvotes"].append(post.score)
                    post_dict["Post Title"].append(post.title)
                    post_dict["Content"].append(post.selftext)
                    post_dict["Url"].append(post.url)
                    post_dict["Author"].append(post.author)

            CHOSE_POST = post_dict["Upvotes"].index(
                max(post_dict["Upvotes"])
            )

            self.PREV_POSTS.append(str(post_dict["Url"][CHOSE_POST]))
            await PREV_CHANNEL.send(post_dict["Url"][CHOSE_POST] + f" {tick()}")

            nEmbed = discord.Embed(title=post_dict["Post Title"][CHOSE_POST],
                                   description=str(post_dict["Content"][CHOSE_POST])[:509] + "...")
            nEmbed.add_field(name="URL", value=post_dict["Url"][CHOSE_POST], inline=False)
            nEmbed.set_thumbnail(url=self.thumb)
            nEmbed.set_footer(text="r/truetf2", icon_url=self.bot.user.avatar_url)
            nEmbed.set_author(name="u/" + str(post_dict["Author"][CHOSE_POST]), icon_url=self.thumb)

            await POST_CHANNEL.send(embed=nEmbed)

            print("Finished! Hibernating.")
            global WAIT_TIME
            WAIT_TIME = self.POST_WAIT
            await redditAPI.close()
            await sleep(WAIT_TIME)
        else:
            await redditAPI.close()
            print("Hibernating.")
            await sleep(WAIT_TIME)


def setup(bot):
    bot.add_cog(RedditPost(bot))
