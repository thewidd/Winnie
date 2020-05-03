import discord
import model.guildConfigs as gf
import roleManagement as rm

class MemberNotifications:
    def __init__(self, bot):
        self.__bot = bot
        self.__registeredChannels = bot.registeredChannels
        self.__guildConfigs = bot.guildConfigs
        self.__roleManagement = bot.roleManagement

    async def notifyIfGamingStateChanged(self, before, after):
        await self.__checkGameSessionStarted(before, after)
        await self.__checkGameSessionEnded(before, after)  

    async def __checkGameSessionStarted(self, before, after):
        await self.__notifyIfChangedPlayingState(after, before, '{} has started playing {}.')

    async def __checkGameSessionEnded(self, before, after):
        await self.__notifyIfChangedPlayingState(before, after, '{} has stopped playing {}.')

    async def __notifyIfChangedPlayingState(self, possibleInGameMember, possibleOutOfGameMember, notificationTextFormat):
        '''
        Send a notification to all registered channels if a user has gone from in-game to out-of-game or vice
        '''    
        possibleInGameIsInGame, inGameActivity = self.__isPlaying(possibleInGameMember)
        possibleOutOfGameIsOutOfGame = not self.__isPlaying(possibleOutOfGameMember)[0]
        # print(f'possibleInGameIsInGame: {possibleInGameIsInGame}, possibleOutOfGameIsOutOfGame: {possibleOutOfGameIsOutOfGame}')

        channelsToNotify = []
        if possibleInGameIsInGame and possibleOutOfGameIsOutOfGame:
            activityForMessage = inGameActivity
            channelsToNotify = [channel for channel in possibleInGameMember.guild.text_channels if channel.id in self.__registeredChannels.getIds()]

        if channelsToNotify:
            # print(f'processing guildId: {possibleInGameMember.guild.id}')
            print(f"Found a change between in-game and out-of-game member updates. Notifying channelIds: [{ ', '.join([str(channel.id) for channel in channelsToNotify]) }]")
            sendText = notificationTextFormat.format(possibleInGameMember.name, activityForMessage.name)
            for channelToNotify in channelsToNotify:
                await channelToNotify.send(sendText)
            
            if self.__guildConfigs.getConfig(possibleInGameMember.guild.id, 'createRoleForPlayersOfGame'):
                await self.__roleManagement.updateRoleForGame(possibleInGameMember, activityForMessage.name)

    def __isPlaying(self, member):
        '''
        Return: tuple of (isPlaying, member.activity object of the playing activity)
        '''
        gameActivities = [activity for activity in member.activities if self.__isPlayingGameActivity(activity)]
        return (len(gameActivities) != 0, next(iter(gameActivities), None))

    def __isPlayingGameActivity(self, activity):
        return (isinstance(activity, discord.Activity) and activity.type == discord.ActivityType.playing) or isinstance(activity, discord.activity.Game)

    
