import discord
from discord.ext import commands, tasks
from time import time as tick
import asyncpraw
import os
from asyncio import sleep
import pymongo

WAIT_TIME = 5


class RedditPost(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ID = os.environ.get("reddit_id")
        self.SECRET = os.environ.get("reddit_secret")
        self.AGENT = os.environ.get("reddit_agent")
        self.URL = os.environ.get("URLstring")
        self.PREV_POSTS = []
        self.POST_WAIT = 3600 * 4  # 4 hours
        self.thumb = "https://cdn.discordapp.com/attachments/389514146053488671/831620871210795079/reddit-logo-16.png"
        self.cluster = pymongo.MongoClient(self.URL)
        self.db = self.cluster["Botputon-Data"]
        self.collection = self.db["RedditData"]

        self.gatherPost.start()

    # Grab the timestamp of the previous post, if has been four hours since the last post, return True for preparing the post.
    async def checkStamp(self, stamp):
        timestamp = stamp["last-tick"]
        print(timestamp)

        if abs(timestamp - tick()) >= self.POST_WAIT:
            return True
        else:  # Otherwise, set the WAIT_TIME variable to the amount of time until the next post is ready.
            global WAIT_TIME
            WAIT_TIME = (timestamp + self.POST_WAIT) - tick()
            return False

    # Make sure the post is not stickied and has not been posted prior.
    async def checkPost(self, thread, prev):
        if not thread.stickied and not (str(thread.author) == "exaflamer") and not (str(thread.url) in prev):
            return True
        return False

    @tasks.loop(seconds=5)
    async def gatherPost(self):

        # Set the filters for later use in the Database
        TICKFILTER = {"last-tick" : {"$exists" : True}}
        PREV_POST_FILTER = {"previous-posts": {"$exists": True}}

        # This works for some things...I guess?
        LTICK = self.collection.find_one({"last-tick": {"$exists": True}})
        POST_CHANNEL = self.bot.get_channel(int(LTICK["target-channel"]))

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

        if await self.checkStamp(LTICK) == True:
            async for post in sub.hot(limit=30):
                if not await self.checkPost(post, self.collection.find_one(PREV_POST_FILTER)["previous-posts"]):
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

            # Update the previous posts and time since last post.
            self.collection.update_one(PREV_POST_FILTER,
                                       {"$push" : {"previous-posts" : f"{str(post_dict['Url'][CHOSE_POST])}" } })
            self.collection.update_one(TICKFILTER, {"$set" : {"last-tick" : tick()} } )
            ## -- Database junk

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
            await self.cluster.close()
            await sleep(WAIT_TIME)
        else:
            await redditAPI.close()
            await self.cluster.close()
            print("Hibernating.")
            await sleep(WAIT_TIME)


def setup(bot):
    bot.add_cog(RedditPost(bot))
