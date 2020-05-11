import json
import threading
from datetime import timedelta

class RegisteredChannels:
    def __init__(self, bot):
        self.bot = bot
        self.__registeredChannelIds = set()

    def _read(self):
        registeredChannelIds = {}
        with open('guildSettings.json') as file:
            try:
                data = json.load(file)
                registeredChannelIds = data['registeredChannelIds']
            except Exception:
                registeredChannelIds = []

        print (json.dumps(registeredChannelIds))
        return registeredChannelIds

    def _write(self, registeredChannelIds):
        with open('guildSettings.json', 'w') as file:
            dataToSave = {'registeredChannelIds': list(registeredChannelIds)}
            json.dump(dataToSave, file)

    def initialize(self):
        self.__registeredChannelIds = set(self._read())

        print(f'Read in {len(self.__registeredChannelIds)} Channels')

        # remove channels that no longer exist
        channelsToRemove = set()
        for channelId in self.__registeredChannelIds:
            if self.bot.get_channel(channelId) == None:
                channelsToRemove.add(channelId)

        self.__registeredChannelIds.difference_update(channelsToRemove)

        self._write(self.__registeredChannelIds) # write the dataStore based on the synced channels
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

    def add(self, channelId: int):
        if channelId not in self.__registeredChannelIds:
            self.__registeredChannelIds.add(channelId)
            self._write(self.__registeredChannelIds)

    def remove(self, channelId: int):
        if channelId in self.__registeredChannelIds:
            self.__registeredChannelIds.remove(channelId)
            self._write(self.__registeredChannelIds)