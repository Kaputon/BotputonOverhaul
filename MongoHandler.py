import pymongo
from os import environ as en


class ClientMongo(pymongo.MongoClient):

    def __init__(self):
        self.url = en.get("URLstring")
        self.client = pymongo.MongoClient(self.url)
        self.db = self.client["Botputon-Data"]

    def handleServer(self, servInfo):
        g_ID = servInfo[0]
        g_NAME = servInfo[1]
        SERVDAT = self.db["ServerData"]

        # If the server is not logged, begin logging it. Otherwise, add one to the server count.
        if not SERVDAT.find_one({"_id": g_ID}):
            SERVDAT.insert_one({"_id": g_ID, "name": g_NAME, "total-posts": 0})
        else:
            SERVDAT.update_one({"_id": g_ID}, {"$inc": {"total-posts": 1}})
        # -------]

    def handleUser(self, guild_ID, userInfo):
        USERDAT = self.db["UserData"]

        guild_ID = str(guild_ID)

        u_ID = userInfo[0]  # User's ID
        u_NAME = userInfo[1]  # Users display name

        USER_FILT = {"_id": u_ID}
        SERV_FILT = {"_id": u_ID, f"{guild_ID}": {"$exists": True}}

        if not USERDAT.find_one(USER_FILT):
            USERDAT.insert_one({"_id": u_ID, "name": u_NAME, f"{guild_ID}": 0})

        # ...if they're in the database, but the server isn't, add the server to their id.
        elif USERDAT.find_one(USER_FILT) and not USERDAT.find_one(SERV_FILT):
            print("Not found")
            USERDAT.update_one(USER_FILT, {"$set": {guild_ID: 1}})

        # If the player and server exist, add 1 post to their ID
        if USERDAT.find_one(SERV_FILT):
            print("Found")
            USERDAT.update_one(USER_FILT, {"$inc": {guild_ID: 1}})

    def returnUser(self, g_ID):
        USERDAT = self.db["UserData"]
        FILTER = {f"{g_ID}": {"$exists": True}}
        CURSOR = USERDAT.find(FILTER)

        post_dictionary = {}

        for record in CURSOR:
            post_dictionary[record["_id"]] = record[f"{g_ID}"]

        return post_dictionary

    def returnServer(self, g_ID):
        SERVDAT = self.db["ServerData"]

        FILTER = {"_id": g_ID}

        SERV = SERVDAT.find_one(FILTER)["total-posts"]

        return SERV
