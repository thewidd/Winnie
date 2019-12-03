import json
import threading
from datetime import timedelta

class RegisteredChannels:
    def __init__(self, bot):
        self.bot = bot
        self.__registeredChannelIds = set()

    def read(self):
        registeredChannelIds = {}
        with open('guildSettings.json') as file:
            try:
                data = json.load(file)
                registeredChannelIds = data['registeredChannelIds']
            except Exception:
                registeredChannelIds = []

        print (json.dumps(registeredChannelIds))
        return registeredChannelIds

    def write(self, registeredChannelIds):
        with open('guildSettings.json', 'w') as file:
            dataToSave = {'registeredChannelIds': list(registeredChannelIds)}
            json.dump(dataToSave, file)

    def initialize(self):
        self.__registeredChannelIds = set(self.read())

        print(f'Read in {len(self.__registeredChannelIds)} Channels')

        # remove channels that no longer exist
        channelsToRemove = set()
        for channelId in self.__registeredChannelIds:
            if self.bot.get_channel(channelId) == None:
                channelsToRemove.add(channelId)

        self.__registeredChannelIds.difference_update(channelsToRemove)

        self.write(self.__registeredChannelIds) # write the dataStore based on the synced channels
        print(f'Number of registered channels after sync: {len(self.__registeredChannelIds)} ')

        oneDay = timedelta(days=1)
        timer = threading.Timer(oneDay.total_seconds(), self.initialize)
        timer.daemon = True
        timer.start()

    def getIds(self):
        return self.__registeredChannelIds

    def __len__(self):
        return len(self.__registeredChannelIds)

    def __contains__(self, key):
        return key in self.__registeredChannelIds

    def add(self, channelId):
        self.__registeredChannelIds.add(channelId)
        self.write(self.__registeredChannelIds)

    def remove(self, channelId):
        self.__registeredChannelIds.remove(channelId)
        self.write(self.__registeredChannelIds)

class RegisteredUsers:
    def __init__(self, bot):
        self.bot = bot
        self.__registeredUserIds = {} # key: userId of members we should notiy about changes. value: set of listening users

    def read(self):
        print('Not implement "read" yet')
        return dict()

    def write(self, registeredUserIds):
        print('Not implemented "write" yet')

    def initialize(self):
        self.__registeredUserIds = self.read()

        print(f'Read in {len(self.__registeredUserIds)} Users')

        # remove users that no longer exist
        usersToRemove = set()
        for userId in self.__registeredUserIds:
            if self.bot.get_user(userId) == None:
                usersToRemove.add(userId)

        for userIdToRemove in usersToRemove:
            self.__registeredUserIds.pop(userIdToRemove)

        self.write(self.__registeredUserIds) # write the dataStore based on the synced users
        print(f'Number of registered users after sync: {len(self.__registeredUserIds)} ')

    def getUserIds(self):
        return self.__registeredUserIds

    def isListeningToUser(self, user, listeningUser):
        try:
            return listeningUser.id in self.__registeredUserIds[user.id]
        except KeyError:
            print('userId is not a registered user for notifications')

    def __len__(self):
        return len(self.__registeredUserIds)

    def __contains__(self, key):
        return key in self.__registeredUserIds

    def add(self, user, listenerUser):
        if user.id not in self.__registeredUserIds:
            self.__registeredUserIds[user.id] = set()
        self.__registeredUserIds[user.id].add(listenerUser.id)
        self.write(self.__registeredUserIds)

    def remove(self, userId, listeningUserId):
        try:
            self.__registeredUserIds[userId].remove(listeningUserId)
            if len(self.__registeredUserIds) == 0:
                self.__registeredUserIds.pop(userId)
        except KeyError:
            print(f"Couldn't find the key for removing listeningUserId: {listeningUserId}, for userId: {userId}")
        self.write(self.__registeredUserIds)